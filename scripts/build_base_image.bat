@echo off
REM Script to build and push the base Docker image to GitHub Container Registry
REM This helps speed up subsequent GitHub Action builds

REM Configuration
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

SET IMAGE_TAG=base
SET FULL_IMAGE_NAME=ghcr.io/%GITHUB_USERNAME%/%GITHUB_REPO%:%IMAGE_TAG%

echo Building and pushing base image as: %FULL_IMAGE_NAME%
echo This may take a while...

REM Build the base image
echo Building base Docker image...
docker build --target base -t %FULL_IMAGE_NAME% -f Dockerfile.dev .

REM Prompt for login
echo Please login to GitHub Container Registry.
echo You'll need a Personal Access Token with 'write:packages' permission.
echo Create one at: https://github.com/settings/tokens
docker login ghcr.io -u %GITHUB_USERNAME%

REM Push the image
echo Pushing base image to GitHub Container Registry...
docker push %FULL_IMAGE_NAME%

echo Base image pushed successfully!
echo Your GitHub Actions builds will now use this as a cache source for faster builds.
