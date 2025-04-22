#!/bin/bash
# Script to build the Docker image in two steps to avoid disk space issues
# First builds a deps-only image, then builds the final image using that as a base

set -e

# Configuration
GITHUB_USERNAME=${1:-"$(git config user.name)"}
GITHUB_REPO=${2:-"$(basename $(git rev-parse --show-toplevel))"}
DEPS_IMAGE_TAG="deps"
FINAL_IMAGE_TAG="latest"
DEPS_IMAGE_NAME="ghcr.io/${GITHUB_USERNAME}/${GITHUB_REPO}:${DEPS_IMAGE_TAG}"
FINAL_IMAGE_NAME="ghcr.io/${GITHUB_USERNAME}/${GITHUB_REPO}:${FINAL_IMAGE_TAG}"

# Check if login information is provided
if [ -z "$GITHUB_USERNAME" ]; then
  echo "Error: GitHub username not provided and couldn't be detected."
  echo "Usage: $0 <github_username> [github_repo]"
  exit 1
fi

echo "Step 1: Creating temporary Dockerfile for dependencies"
cat > Dockerfile.deps << EOF
FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

ENV PYTHONUNBUFFERED=1 \\
    DEBIAN_FRONTEND=noninteractive

# Install minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    python3-pip \\
    python3-wheel \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Install dependencies but don't copy application code
RUN pip install --no-cache-dir wheel setuptools packaging
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
RUN pip install --no-cache-dir -r requirements.txt
EOF

echo "Step 2: Building deps-only image"
docker build -t $DEPS_IMAGE_NAME -f Dockerfile.deps .

echo "Step 3: Creating final Dockerfile"
cat > Dockerfile.final << EOF
FROM $DEPS_IMAGE_NAME

# Copy the application code
COPY . .

# Create output directory
RUN mkdir -p /app/outputs /app/hf_download

# Set environment variables for Hugging Face
ENV HF_HOME=/app/hf_download

# Expose the default Gradio port
EXPOSE 7860

# Run the application
CMD ["python3", "demo_gradio.py", "--server", "0.0.0.0", "--port", "7860"]
EOF

echo "Step 4: Building final image"
docker build -t $FINAL_IMAGE_NAME -f Dockerfile.final .

echo "Step 5: Login to GitHub Container Registry"
echo "Please login to GitHub Container Registry."
echo "You'll need a Personal Access Token with 'write:packages' permission."
echo "Create one at: https://github.com/settings/tokens"
docker login ghcr.io -u $GITHUB_USERNAME

echo "Step 6: Pushing deps image"
docker push $DEPS_IMAGE_NAME

echo "Step 7: Pushing final image"
docker push $FINAL_IMAGE_NAME

echo "Build and push completed successfully!"
echo "Your images are now available at:"
echo "  - $DEPS_IMAGE_NAME"
echo "  - $FINAL_IMAGE_NAME"
