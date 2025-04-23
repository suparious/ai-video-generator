#!/bin/bash
set -e

# Configuration
GITHUB_USERNAME=${GITHUB_USERNAME:-"shaun.prince"}
IMAGE_NAME="ai-video-generator"
VERSION=${VERSION:-$(date +"%Y%m%d%H%M")}
GHCR_PAT=${GHCR_PAT:-""}  # GitHub Personal Access Token with packages:write

# Show configuration
echo "======== Configuration ========"
echo "GitHub Username: $GITHUB_USERNAME"
echo "Image Name: $IMAGE_NAME"
echo "Version: $VERSION"
echo "GitHub PAT: ${GHCR_PAT:+set (value hidden)}"
echo "=============================="

# Check if GHCR_PAT is set
if [ -z "$GHCR_PAT" ]; then
    echo "ERROR: GitHub Personal Access Token (GHCR_PAT) is not set."
    echo "Please set it with: export GHCR_PAT='your_github_token'"
    echo "Your PAT needs 'write:packages' permission."
    exit 1
fi

# Full image reference
FULL_IMAGE_NAME="ghcr.io/$GITHUB_USERNAME/$IMAGE_NAME"

# Login to GitHub Container Registry
echo "Logging in to GitHub Container Registry..."
echo "$GHCR_PAT" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin

# Build Docker image with version tag
echo "Building Docker image..."
cd "$(dirname "$0")/.." || exit
docker build -t "$FULL_IMAGE_NAME:$VERSION" -t "$FULL_IMAGE_NAME:latest" -f docker/Dockerfile .

# Push image to GitHub Container Registry
echo "Pushing image to GitHub Container Registry..."
docker push "$FULL_IMAGE_NAME:$VERSION"
docker push "$FULL_IMAGE_NAME:latest"

echo "✅ Successfully published $FULL_IMAGE_NAME:$VERSION to GitHub Container Registry"
echo "✅ Also tagged as $FULL_IMAGE_NAME:latest"
