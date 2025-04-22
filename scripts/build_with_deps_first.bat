REM Example usage: build_with_deps_first.bat suparious ai-video-generator

@echo off
REM Script to build the Docker image in two steps to avoid disk space issues
REM First builds a deps-only image, then builds the final image using that as a base

SET GITHUB_USERNAME=%1
SET GITHUB_REPO=%2

IF "%GITHUB_USERNAME%"=="" (
  echo Error: GitHub username not provided.
  echo Usage: %0 ^<github_username^> [github_repo]
  exit /b 1
)

IF "%GITHUB_REPO%"=="" (
  FOR %%I IN ("%CD%") DO SET GITHUB_REPO=%%~nxI
)

SET DEPS_IMAGE_TAG=deps
SET FINAL_IMAGE_TAG=latest
SET DEPS_IMAGE_NAME=ghcr.io/%GITHUB_USERNAME%/%GITHUB_REPO%:%DEPS_IMAGE_TAG%
SET FINAL_IMAGE_NAME=ghcr.io/%GITHUB_USERNAME%/%GITHUB_REPO%:%FINAL_IMAGE_TAG%

echo Step 1: Creating temporary Dockerfile for dependencies
(
echo FROM nvidia/cuda:12.8.0-devel-ubuntu22.04
echo.
echo ENV PYTHONUNBUFFERED=1 \
echo     DEBIAN_FRONTEND=noninteractive
echo.
echo # Install minimal dependencies
echo RUN apt-get update ^&^& apt-get install -y --no-install-recommends \
echo     python3-pip \
echo     python3-wheel \
echo     ^&^& apt-get clean \
echo     ^&^& rm -rf /var/lib/apt/lists/*
echo.
echo WORKDIR /app
echo COPY requirements.txt .
echo.
echo # Install dependencies but don't copy application code
echo RUN pip install --no-cache-dir wheel setuptools packaging
echo RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
echo RUN pip install --no-cache-dir -r requirements.txt
) > Dockerfile.deps

echo Step 2: Building deps-only image
docker build -t %DEPS_IMAGE_NAME% -f Dockerfile.deps .

echo Step 3: Creating final Dockerfile
(
echo FROM %DEPS_IMAGE_NAME%
echo.
echo # Copy the application code
echo COPY . .
echo.
echo # Create output directory
echo RUN mkdir -p /app/outputs /app/hf_download
echo.
echo # Set environment variables for Hugging Face
echo ENV HF_HOME=/app/hf_download
echo.
echo # Expose the default Gradio port
echo EXPOSE 7860
echo.
echo # Run the application
echo CMD ["python3", "demo_gradio.py", "--server", "0.0.0.0", "--port", "7860"]
) > Dockerfile.final

echo Step 4: Building final image
docker build -t %FINAL_IMAGE_NAME% -f Dockerfile.final .

echo Step 5: Login to GitHub Container Registry
echo Please login to GitHub Container Registry.
echo You'll need a Personal Access Token with 'write:packages' permission.
echo Create one at: https://github.com/settings/tokens
docker login ghcr.io -u %GITHUB_USERNAME%

echo Step 6: Pushing deps image
docker push %DEPS_IMAGE_NAME%

echo Step 7: Pushing final image
docker push %FINAL_IMAGE_NAME%

echo Build and push completed successfully!
echo Your images are now available at:
echo   - %DEPS_IMAGE_NAME%
echo   - %FINAL_IMAGE_NAME%
