# Simplified Docker Setup for FramePack AI Video Generator

This guide explains the recommended approach for building and distributing the Docker image for FramePack AI Video Generator.

## Overview

We use a two-step approach:
1. First, build a base image locally that contains all dependencies
2. Then, GitHub Actions uses this base image as a cache source for faster builds

## Building the Base Image (Recommended)

The most reliable approach is to build the base image locally first, then push it to GitHub Container Registry:

```bash
# On Windows
scripts\build_base_image.bat YOUR_GITHUB_USERNAME

# On Linux/macOS
chmod +x scripts/build_base_image.sh
./scripts/build_base_image.sh YOUR_GITHUB_USERNAME
```

This script:
1. Builds a base image with all Python dependencies and CUDA support
2. Pushes this base image to GitHub Container Registry with tag `:base`
3. Takes about 10 minutes to complete

## GitHub Actions Automated Build

Once the base image is pushed, any commits to the main branch will trigger the GitHub Actions workflow, which:
1. Uses your pre-built base image as a cache source
2. Builds the final Docker image much faster
3. Tags and pushes the image to GitHub Container Registry

## For Users: Using the Published Docker Image

Users can pull and use the pre-built Docker image:

```bash
# Pull the image
docker pull ghcr.io/YOUR_USERNAME/ai-video-generator:latest

# Run with NVIDIA GPU support
docker run --gpus all -p 7860:7860 \
  -v "$(pwd)/outputs:/app/outputs" \
  -v "$(pwd)/hf_download:/app/hf_download" \
  ghcr.io/YOUR_USERNAME/ai-video-generator:latest
```

## Alternative: Using Docker Compose

Users can also use Docker Compose for easier management:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-video-generator.git
cd ai-video-generator

# Start the container
docker-compose up -d
```

## Troubleshooting

If you encounter issues with the GitHub Actions workflow timing out, you can:

1. Build and push the complete image locally using:
   ```bash
   docker build -t ghcr.io/YOUR_USERNAME/ai-video-generator:latest .
   docker push ghcr.io/YOUR_USERNAME/ai-video-generator:latest
   ```

2. Or check the logs for specific errors and try one of the alternative workflows:
   ```bash
   # For a different build approach using a multi-stage process
   scripts\build_with_deps_first.bat YOUR_GITHUB_USERNAME ai-video-generator
   ```
