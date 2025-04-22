# Docker Setup Guide for FramePack AI Video Generator

This guide explains how to use the FramePack AI Video Generator with Docker.

## Requirements

- Docker installed on your system ([Docker installation guide](https://docs.docker.com/get-docker/))
- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit installed ([Installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html))

## Using Pre-built Docker Image

The easiest way to get started is to use our pre-built Docker image, which is automatically published to GitHub Container Registry.

```bash
# Pull the Docker image
docker pull ghcr.io/suparious/ai-video-generator:latest

# Create directories for persistent storage
mkdir -p outputs hf_download

# Run the container
docker run --gpus all -p 7860:7860 \
  -v "$(pwd)/outputs:/app/outputs" \
  -v "$(pwd)/hf_download:/app/hf_download" \
  ghcr.io/suparious/ai-video-generator:latest
```

After running this command, you can access the application at http://localhost:7860 in your web browser.

## Using Docker Compose

An alternative approach is to use Docker Compose, which simplifies container management.

1. Clone the repository:
   ```bash
   git clone https://github.com/suparious/ai-video-generator.git
   cd ai-video-generator
   ```

2. Start the container:
   ```bash
   docker-compose up -d
   ```

3. Access the application at http://localhost:7860

4. To stop the container:
   ```bash
   docker-compose down
   ```

## Building the Docker Image Locally

If you prefer to build the Docker image yourself:

```bash
# Clone the repository
git clone https://github.com/suparious/ai-video-generator.git
cd ai-video-generator

# Build the image
docker build -t ai-video-generator .

# Run the container
docker run --gpus all -p 7860:7860 \
  -v "$(pwd)/outputs:/app/outputs" \
  -v "$(pwd)/hf_download:/app/hf_download" \
  ai-video-generator
```

## Important Notes

1. **Data Persistence**:
   - The `/app/outputs` directory stores generated videos
   - The `/app/hf_download` directory caches downloaded models from HuggingFace

2. **GPU Requirements**:
   - The container requires NVIDIA GPU with CUDA support
   - Make sure you have the NVIDIA Container Toolkit properly configured

3. **Memory Requirements**:
   - The application requires at least 6GB of GPU memory
   - For longer videos or higher quality settings, more memory is recommended

4. **Port Configuration**:
   - The default port is 7860
   - To use a different port (e.g., 8080), modify the command:
     ```bash
     docker run --gpus all -p 8080:7860 ...
     ```

## Troubleshooting

1. **NVIDIA GPU not detected**:
   - Verify that your NVIDIA drivers are installed correctly
   - Ensure NVIDIA Container Toolkit is properly installed
   - Try running: `docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu22.04 nvidia-smi`

2. **Out of Memory errors**:
   - Increase the "GPU Memory Preservation" setting in the web interface
   - Try using the TeaCache option to reduce memory usage

3. **Container exits immediately**:
   - Check Docker logs: `docker logs [container_id]`
   - Ensure your GPU has enough memory and supports CUDA
