# Publishing to GitHub Container Registry (ghcr.io)

This document explains how to build and publish the FramePack AI Video Generator Docker image to GitHub Container Registry (ghcr.io).

## Prerequisites

1. **GitHub Account**: You need a GitHub account where you want to publish the image
2. **GitHub Personal Access Token (PAT)**:
   - Create a new [Personal Access Token](https://github.com/settings/tokens) with `write:packages` permission
   - This token will be used to authenticate with the GitHub Container Registry

## Publishing from Local Machine

### Using Bash Script (Linux/macOS/WSL)

1. Set the required environment variables:

```bash
export GITHUB_USERNAME="your-github-username"
export GHCR_PAT="your-personal-access-token"
export VERSION="1.0.0"  # Optional: defaults to timestamp
```

2. Run the publish script:

```bash
chmod +x scripts/publish_to_ghcr.sh
./scripts/publish_to_ghcr.sh
```

### Using Batch Script (Windows)

1. Set the required environment variables:

```cmd
set GITHUB_USERNAME=your-github-username
set GHCR_PAT=your-personal-access-token
set VERSION=1.0.0  # Optional: defaults to timestamp
```

2. Run the publish script:

```cmd
scripts\publish_to_ghcr.bat
```

## Pulling the Published Image

Once published, you can pull the image using:

```bash
docker pull ghcr.io/your-github-username/ai-video-generator:latest
```

## Running the Published Image

Run the published image using:

```bash
docker run -d --gpus all -p 7860:7860 \
  -v ./outputs:/app/outputs \
  -v ./hf_download:/app/hf_download \
  -v ./static:/app/static \
  -e HF_TOKEN="your-huggingface-token" \
  ghcr.io/your-github-username/ai-video-generator:latest
```

Or with docker-compose:

```bash
# Create a docker-compose.override.yml file
cat > docker-compose.override.yml << EOL
services:
  ai-video-generator:
    image: ghcr.io/your-github-username/ai-video-generator:latest
    build:
      context: .
      dockerfile: docker/Dockerfile
EOL

# Run with docker-compose
docker-compose up -d
```

## Making Your Package Public

By default, packages published to GitHub Container Registry are private. To make your package public:

1. Go to your GitHub profile
2. Click on "Packages"
3. Select your `ai-video-generator` package
4. Click on "Package settings"
5. Under "Danger Zone", click "Change visibility"
6. Select "Public" and confirm

## Creating a GitHub Release

To associate your Docker image with a GitHub release:

1. Create a new release in your GitHub repository
2. Set the tag version to match the Docker image version
3. Add release notes and documentation
4. Link to the Docker image in the release notes:

```
Docker image: ghcr.io/your-github-username/ai-video-generator:1.0.0
```

## Troubleshooting

- **Authentication Issues**: Make sure your PAT has the correct permissions
- **Build Failures**: Check Docker build logs for errors
- **Push Failures**: Ensure you have write access to the repository/organization
