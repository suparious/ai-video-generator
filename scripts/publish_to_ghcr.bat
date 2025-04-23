@echo off
setlocal enabledelayedexpansion

:: Configuration (set these variables or set them as environment variables before running)
if not defined GITHUB_USERNAME set GITHUB_USERNAME=shaun.prince
set IMAGE_NAME=ai-video-generator
if not defined VERSION for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (
    for /f "tokens=1-2 delims=: " %%i in ('time /t') do (
        set VERSION=%%c%%a%%b%%i%%j
    )
)
:: GHCR_PAT should be set as an environment variable for security
if not defined GHCR_PAT (
    echo ERROR: GitHub Personal Access Token (GHCR_PAT) is not set.
    echo Please set it with: set GHCR_PAT=your_github_token
    echo Your PAT needs 'write:packages' permission.
    exit /b 1
)

:: Show configuration
echo ======== Configuration ========
echo GitHub Username: %GITHUB_USERNAME%
echo Image Name: %IMAGE_NAME%
echo Version: %VERSION%
echo GitHub PAT: !GHCR_PAT:~0,1!****** (hidden)
echo ==============================

:: Full image reference
set FULL_IMAGE_NAME=ghcr.io/%GITHUB_USERNAME%/%IMAGE_NAME%

:: Login to GitHub Container Registry
echo Logging in to GitHub Container Registry...
echo %GHCR_PAT% | docker login ghcr.io -u %GITHUB_USERNAME% --password-stdin

:: Build Docker image with version tag
echo Building Docker image...
cd %~dp0\..
docker build -t %FULL_IMAGE_NAME%:%VERSION% -t %FULL_IMAGE_NAME%:latest -f docker/Dockerfile .

:: Push image to GitHub Container Registry
echo Pushing image to GitHub Container Registry...
docker push %FULL_IMAGE_NAME%:%VERSION%
docker push %FULL_IMAGE_NAME%:latest

echo ✅ Successfully published %FULL_IMAGE_NAME%:%VERSION% to GitHub Container Registry
echo ✅ Also tagged as %FULL_IMAGE_NAME%:latest

endlocal
