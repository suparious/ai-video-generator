#!/bin/bash

# Script to extract wheels from a Python virtualenv for Docker
# Usage: ./extract_wheels.sh /path/to/your/virtualenv

VENV_PATH=$1

# Check if virtualenv path was provided
if [ -z "$VENV_PATH" ]; then
    echo "Error: Please provide the path to your virtualenv."
    echo "Usage: ./extract_wheels.sh /path/to/your/virtualenv"
    exit 1
fi

# Check if the provided path is a valid virtualenv
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "Error: The provided path does not appear to be a valid virtualenv."
    echo "Could not find $VENV_PATH/bin/activate"
    exit 1
fi

# Create wheels directory
mkdir -p wheels

# Extract wheels from pip cache
echo "Extracting wheels from pip cache..."
source "$VENV_PATH/bin/activate"
CACHE_DIR=$(pip cache dir)
echo "Pip cache directory: $CACHE_DIR"

# Copy wheels of interest (common ones that are difficult to compile)
echo "Copying wheels of special interest to wheels/ directory..."
find "$CACHE_DIR" -name "flash_attn*.whl" -exec cp {} wheels/ \;
find "$CACHE_DIR" -name "xformers*.whl" -exec cp {} wheels/ \;
find "$CACHE_DIR" -name "triton*.whl" -exec cp {} wheels/ \;
find "$CACHE_DIR" -name "sentencepiece*.whl" -exec cp {} wheels/ \;

# If not found in cache, try downloading them if they're installed
echo "Downloading wheels that weren't found in cache..."
if pip list | grep -q flash-attn; then
    pip download --only-binary :all: --dest wheels/ flash-attn
fi

if pip list | grep -q xformers; then
    pip download --only-binary :all: --dest wheels/ xformers
fi

if pip list | grep -q triton; then
    pip download --only-binary :all: --dest wheels/ triton
fi

if pip list | grep -q sentencepiece; then
    pip download --only-binary :all: --dest wheels/ sentencepiece
fi

# Create requirements.txt
echo "Creating requirements.txt from virtualenv..."
pip freeze > requirements.txt

# Count wheels
WHEEL_COUNT=$(ls -1 wheels/ | wc -l)
echo "----------------------------------------"
echo "Successfully extracted $WHEEL_COUNT wheels to the wheels/ directory."
echo "requirements.txt has been created."
echo ""
echo "You can now build your Docker image with:"
echo "docker-compose build"
echo "----------------------------------------"

deactivate
