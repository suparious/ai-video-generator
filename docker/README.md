# Docker Setup for FramePack AI Video Generator

This document explains how to use Docker to run the FramePack AI Video Generator with CUDA 12.8 and PyTorch 2.8.0.

## Prerequisites

- A CUDA-compatible GPU
- [Docker](https://docs.docker.com/get-docker/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) (for GPU support)
  - For Windows: [Docker Desktop with WSL 2 backend](https://docs.docker.com/desktop/install/windows-install/) and [NVIDIA CUDA on WSL](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)

## Quick Start

### Step 1: Download Models (First Time Only)

Before running the container for the first time, download the required models:

```bash
# First, install dependencies according to the main README.md
# See: README.md for the complete setup instructions

# Then download models (uses HF_TOKEN from environment if available)
python download_models.py

# Or specify a token directly
python download_models.py --token YOUR_HF_TOKEN
```

> **Note:** Using a Hugging Face token (`HF_TOKEN`) significantly speeds up model downloads. For convenience, consider adding it to your environment variables in `/etc/environment` on Linux or system environment variables on Windows.

This process may take some time (around 15-20 minutes depending on your internet speed) but only needs to be done once. It downloads approximately 7GB of model files.

### Step 2: Build and Run the Docker Container

Build and start the container using docker-compose:

```bash
docker-compose up -d
```

Compiling the wheels in python can sometimes take around 3-5hours on a 6th generation Intel i7.

### Step 3: Access the Interface

Access the Gradio interface in your browser:

```
http://localhost:7860
```

### Additional Commands

**View logs:**

```bash
docker-compose logs -f
```

**Stop the container:**

```bash
docker-compose down
```

## Directory Structure

The Docker setup mounts several volumes to persist data:

- `./outputs`: Generated videos will be saved here
- `./hf_download`: Hugging Face model cache (40GB+)
- `./static`: Custom CSS and static files
- `./wheels`: Directory for custom-compiled wheels

## Handling Large Model Files

The Hugging Face model files are very large (40GB+) and should not be included in the Docker image. Instead, they are mounted as a volume. There are two approaches:

### Approach 1: Pre-download Models (Recommended)

Use the provided script to download models before running Docker:

```bash
# First, install dependencies according to the main README.md
# See: README.md for the complete setup instructions

# Then download models (uses HF_TOKEN from environment if available)
python download_models.py

# Or specifying a token directly
python download_models.py --token YOUR_HF_TOKEN
```

This creates a `hf_download` directory with all required models, which is then mounted into the container.

### Approach 2: Download at Runtime

If you don't pre-download models, they will be downloaded the first time you run the container. This can be slow and requires internet access at runtime.

To speed up subsequent runs, the models are cached in the mounted `hf_download` directory.

The container automatically uses your `HF_TOKEN` from the environment if available.

### Managing Model Cache Size

If disk space is a concern:

1. Delete unused model versions in `hf_download/hub/models/`
2. Keep only the specific model versions used by the application
3. Consider using a larger drive for the model cache and adjust the volume mount path in `docker-compose.yml`

## Custom Wheels

If you need custom-compiled wheels (like for `flash-attn`, `xformers`, etc.), please refer to the main README.md for setting up your environment first. Once you have your environment set up according to the instructions in README.md, you can extract the wheels for Docker:

### For Linux Users

You can use the provided script to extract wheels from an existing virtualenv:

```bash
chmod +x extract_wheels.sh
./extract_wheels.sh /path/to/your/virtualenv
```

### For Windows Users

1. Create a `wheels` directory if it doesn't exist:

```cmd
mkdir wheels
```

2. Copy your custom wheels to this directory. These are typically found in your pip cache directory. For Python 3.13.3, you would look for files like:

```
wheels/
├── flash_attn-2.7.4.post1-cp313-cp313-linux_x86_64.whl
├── sentencepiece-0.2.0-cp313-cp313-linux_x86_64.whl
└── xformers-0.0.29.post3-cp313-cp313-linux_x86_64.whl
```

You can find your pip cache location by running:

```cmd
pip cache dir
```

3. Alternatively, you can manually download the wheels from PyPI or other sources and place them in the wheels directory.

```
ai-video-generator/
├── wheels/
│   ├── flash_attn-2.7.4.post1-cp313-cp313-linux_x86_64.whl
│   ├── sentencepiece-0.2.0-cp313-cp313-linux_x86_64.whl
│   └── xformers-0.0.29.post3-cp313-cp313-linux_x86_64.whl
```

## Modifying the Configuration

You can adjust the configuration by editing `config.py` before building the Docker image.

## Building for Different Environments

### High-VRAM Configuration

For systems with high VRAM (24GB+), you may want to adjust the Dockerfile:

```dockerfile
# In Dockerfile, after installing requirements
ENV HIGH_VRAM=1
```

### Low-VRAM Configuration

For systems with limited VRAM, the default configuration should work well as it includes memory optimization techniques.

## Troubleshooting

### CUDA Issues

If you encounter CUDA-related errors, make sure:

1. Your NVIDIA drivers are up-to-date
2. The NVIDIA Container Toolkit is properly installed
3. You can run `nvidia-smi` successfully on your host machine

#### Windows-Specific CUDA Troubleshooting

For Windows users with WSL 2:

1. Ensure you have the latest NVIDIA drivers installed for Windows
2. Make sure WSL 2 is properly configured with CUDA support
3. Inside your WSL 2 distribution, check that NVIDIA drivers are working:

```bash
nvidia-smi
```

4. If using Docker Desktop, ensure that WSL 2 integration is enabled for your Linux distribution

### Out of Memory Errors

If you experience OOM (Out of Memory) errors:

1. Increase the `gpu_memory_preservation` setting in the UI
2. Decrease the `total_second_length` or `latent_window_size` parameters
3. Try disabling TeaCache in the UI

### Docker Image Size Issues

The Docker image is large due to CUDA, PyTorch, and model files. If disk space is a concern:

1. Use an external volume for the Hugging Face models
2. Periodically clean Docker's unused images with `docker system prune`

## Windows WSL 2 Setup Tips

1. **Memory Allocation**: By default, WSL 2 might not allocate enough memory for deep learning tasks. Create or modify the `.wslconfig` file in your Windows user directory:

```
# %UserProfile%\.wslconfig
[wsl2]
memory=16GB
processors=8
```

2. **Docker Desktop Settings**: Make sure in Docker Desktop settings:
   - Under Resources > WSL Integration, enable integration with your Linux distribution
   - Under Resources > GPU, ensure NVIDIA GPU is enabled

3. **File Access**: For better performance, store your project files in the Linux filesystem, not on Windows-mounted drives

4. **Port Forwarding**: WSL 2 automatically forwards ports, so you can access the Gradio interface on `localhost:7860` from your Windows browser
