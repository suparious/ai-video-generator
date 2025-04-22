# FramePack AI Video Generator

FramePack is an advanced AI video generator based on next-frame prediction technology. It implements the architecture described in ["Packing Input Frame Context in Next-Frame Prediction Models for Video Generation"](https://arxiv.org/abs/2504.12626) (Zhang & Agrawala, 2025).

## Key Features

- **Progressive Video Generation**: Creates videos by predicting frames sequentially with inverted anti-drifting sampling
- **Efficient Memory Usage**: Compresses input contexts to a constant length regardless of video length
- **Laptop-Friendly**: Can process long videos with 13B models even on modest laptop GPUs (6GB VRAM)
- **High Quality Results**: Produces temporally consistent, high-quality video animations from a single image
- **Optimized for Hand Details**: Special mode to improve hand and fine detail quality
- **Content-Specific Flow Shift**: Optimized diffusion schedulers for different types of motion

## Requirements

Note that this repo is a functional desktop software with minimal standalone high-quality sampling system and memory management.

- Nvidia GPU in RTX 30XX, 40XX, 50XX series that supports fp16 and bf16. The GTX 20XX are not tested and the GTX 10XX probably wont work.
- Linux or Windows operating system.
- At least 6GB GPU memory.

To generate 1-minute video (60 seconds) at 30fps (1800 frames) using 13B model, the minimal required GPU memory is 6GB. (Yes 6 GB, not a typo. Laptop GPUs are okay.)

About speed, on the RTX 4090 desktop it generates at a speed of 2.5 seconds/frame (unoptimized) or 1.5 seconds/frame (teacache). On laptops like 3070ti laptop or 3060 laptop, it is about 4x to 8x slower.

In any case, you will directly see the generated frames since it is next-frame(-section) prediction. So you will get lots of visual feedback before the entire video is generated. The video usually generates from reverse.

## Installation

### Option 1: Using Docker

#### Prerequisites
- Docker installed
- NVIDIA Docker support (nvidia-container-toolkit)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or manually with Docker
docker build -t ai-video-generator .
docker run --gpus all -p 7860:7860 -v "$(pwd)/outputs:/app/outputs" -v "$(pwd)/hf_download:/app/hf_download" ai-video-generator
```

Access the application at http://localhost:7860

You can also pull the image from GitHub Container Registry:

```bash
docker pull ghcr.io/suparious/ai-video-generator:latest
docker run --gpus all -p 7860:7860 -v "$(pwd)/outputs:/app/outputs" -v "$(pwd)/hf_download:/app/hf_download" ghcr.io/suparious/ai-video-generator:latest
```

### Option 2: Manual Installation

On a Debian / Ubuntu system, install dev dependencies:

```bash
sudo apt update

sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

sudo apt install -y python3-full python3-pip python3-wheel python3-venv

sudo apt install -y libavutil-dev libavformat-dev libavcodec-dev libavdevice-dev libavfilter-dev libswscale-dev gfortran libopenblas-dev cmake libxsimd-dev

sudo apt install -y llvm
```

We recommend having an independent Python 3.13 virtual environment, using [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#a-getting-pyenv).

- Explicitly setup your torch ahead of the requirements, if you have special needs, such as ROCm or older / newer NVIDIA, then adjust this command appropriately. For standard NVIDIA Cuda 12.6 use:

  `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126`

For the latest NVIDIA Cuda 12.8:

  `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128`

- It is highly recommended to run as a local user and not root. To do this you will need `wheel` and a few other setup and packaging tools:

  `pip install wheel setuptools packaging`

- Then install requirements the normal way:

  `pip install -r requirements.txt`

To start the GUI, run:

`python demo_gradio.py`

Note that it supports `--share`, `--port`, `--server`, and so on.

The software supports PyTorch attention, xformers, flash-attn, sage-attention. By default, it will just use PyTorch attention. You can install those attention kernels if you know how. If you have problems with the defaults, comment them out form the `requirements.txt`.

For example, to install a specific version of sage-attention, comment it out from the `requirements.txt` and then run:

`pip install sageattention==1.0.6`

However, you are highly recommended to first try without sage-attention since it will influence results, though the influence is minimal.

Building the wheels for all of these kernels can take a long time.

## GUI Guide

### Basic Usage

1. **Upload an Image**: On the left side, upload a starting image for your video
2. **Enter a Prompt**: Describe the motion or action you want the subject to perform
3. **Select a Preset**: Choose from preset configurations optimized for different types of motion
4. **Adjust Settings**: Fine-tune parameters as needed (or leave as default)
5. **Start Generation**: Click "Start Generation" to begin the process

### Advanced Features

#### Preset Configurations

The interface includes several presets optimized for different types of videos:

- **Default**: Balanced settings suitable for general use
- **Dance**: Optimized for dance movements with TeaCache disabled for better hand details and specialized flow shift parameters
- **Talking**: Fine-tuned for facial expressions and talking animations with optimized flow shift for facial motion
- **Action**: Enhanced settings for dynamic movements and actions with flow parameters tuned for fast motion
- **Subtle Movement**: Gentler settings for minimal, gradual movements with less aggressive flow shift parameters

#### TeaCache & Hand Optimization

TeaCache is a speed optimization technique that can make generation 1.5-2x faster, but may affect detail quality for hands and fingers. Two options are provided:

- **Use TeaCache**: Enable for faster generation (recommended for most cases)
- **Optimize for Hands/Details**: When enabled with TeaCache, this uses modified settings that better preserve fine details like hands and fingers while still maintaining speed benefits

For videos with extensive hand movements or fine details, either disable TeaCache completely or enable Hand Optimization.

#### Understanding the Generation Process

This model uses inverted anti-drifting sampling, which means:

1. The ending frames are generated first, followed by earlier frames
2. Progress visualization shows the current section being generated
3. The video will appear to be "filled in" from end to beginning
4. Initial progress may be slower as the device warms up

## Prompting Guidelines

### Effective Prompt Structure

For best results, use concise, motion-focused prompts that follow this structure:

1. **Identify the subject** ("The person", "The woman", "The man")
2. **Describe the motion** (dancing, talking, walking, etc.)
3. **Add qualifiers** (gracefully, powerfully, slowly, etc.)
4. **Optional details** (environment, mood, style)

### Example Prompts by Category

**Dance Movements:**

- "The person dances gracefully, with clear movements, full of charm."
- "The person performs a spinning motion with arms extended."

**Talking/Expressions:**

- "The person talks animatedly, using hand gestures to emphasize points."
- "The person smiles and nods, maintaining eye contact."

**Hand-Focused Actions:**

- "The person plays an invisible piano with detailed finger movements."
- "The person waves hello with a friendly smile."
- "The person gestures with hands while explaining a concept."

**Subtle Movements:**

- "The person makes subtle movements, with a calm expression."
- "The person breathes slowly, barely moving, with a peaceful demeanor."

### AI-Assisted Prompting

You can use this ChatGPT template to generate effective prompts from images:

```plaintext
You are an assistant that writes short, motion-focused prompts for animating images.

When the user sends an image, respond with a single, concise prompt describing visual motion (such as human activity, moving objects, or camera movements). Focus only on how the scene could come alive and become dynamic using brief phrases.

Larger and more dynamic motions (like dancing, jumping, running, etc.) are preferred over smaller or more subtle ones (like standing still, sitting, etc.).

Describe subject, then motion, then other things. For example: "The person dances gracefully, with clear movements, full of charm."

If there is something that can dance (like a man, girl, robot, etc.), then prefer to describe it as dancing.

Stay in a loop: one image in, one motion prompt out. Do not explain, ask questions, or generate multiple options.
```

### Tips for Specific Scenarios

- **For hand/finger movements**: Use explicit hand-related descriptions and disable TeaCache or enable Hand Optimization
- **For smoother videos**: Use longer prompts that describe the motion flow from start to finish
- **For complex actions**: Break down the motion into simple components

## Advanced Settings Guide

### Performance Settings

- **TeaCache**: Speeds up generation by 1.5-2x. May slightly reduce detail quality in hands and fine features.
- **Hand Optimization**: When used with TeaCache, this increases the TeaCache threshold to better preserve fine details.
- **GPU Memory Preservation**: Increase this value if you encounter Out-of-Memory errors. Higher values mean slower processing but less chance of memory issues.
- **MP4 Compression Quality**: Controls the compression of the output video. Lower values (15-20) offer good quality with reasonable file sizes.

### Generation Settings

- **Diffusion Steps**: More steps generally produce higher quality results at the cost of generation time. 25-30 is recommended for most purposes.
- **Guidance Scale**: Controls how strongly the generation follows the prompt. Higher values (10-15) give stronger adherence to the prompt but may reduce naturalness.
- **Flow Shift Preset**: Optimizes the diffusion schedule for specific types of content. Different presets are tuned for dance, talking, subtle movements, and hand details.
- **Total Video Length**: Sets the target length of the final video. Longer videos take proportionally more time to generate.

## Troubleshooting

### Common Issues

- **Poor Hand/Finger Detail**: Disable TeaCache or enable Hand Optimization
- **Out of Memory Errors**: Increase GPU Memory Preservation value
- **Black Video Output**: Try changing MP4 Compression to 16 if you see black output videos
- **Missing Beginning of Video**: Be patient! Due to inverted sampling, the beginning is generated last
- **Slow Generation**: This is normal for the first few frames as models load and optimize

## Citation

```bibtex
@article{zhang2025framepack,
  title={Packing Input Frame Contexts in Next-Frame Prediction Models for Video Generation},
  author={Zhang, Lvmin and Agrawala, Maneesh},
  journal={arXiv preprint arXiv:2504.12626},
  year={2025}
}
```
