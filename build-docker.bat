@echo off
REM Script to build the Docker image without using cache

REM Force a clean build
docker build --no-cache -t ai-video-generator .

echo Build completed. You can run the container with:
echo docker run --gpus all -p 7860:7860 -v "./outputs:/app/outputs" -v "./hf_download:/app/hf_download" ai-video-generator
