# FramePack AI Video Generator - Quick Start Guide

This guide will help you quickly get started with the FramePack AI Video Generator, a powerful tool that can create smooth, high-quality videos from a single image.

## Installation

### 1. System Requirements

- **GPU**: NVIDIA RTX series (30XX, 40XX, 50XX) with at least 6GB VRAM
- **OS**: Windows or Linux
- **Python**: 3.13 recommended

### 2. Install Dependencies

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
sudo apt install -y python3-full python3-pip python3-wheel python3-venv
sudo apt install -y libavutil-dev libavformat-dev libavcodec-dev libavdevice-dev libavfilter-dev libswscale-dev gfortran libopenblas-dev cmake libxsimd-dev
sudo apt install -y llvm
```

### 3. Setup Python Environment

```bash
# Create and activate virtual environment (recommended)
python -m venv framepack-env
source framepack-env/bin/activate  # Linux/Mac
# or
framepack-env\Scripts\activate  # Windows

# Install PyTorch first (for CUDA 12.6)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# Install basic requirements
pip install wheel setuptools packaging

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
python demo_gradio.py
```

Additional options:
- `--server 127.0.0.1` - Run locally
- `--share` - Create a public URL
- `--inbrowser` - Open in browser automatically
- `--port 7860` - Specify port

## Basic Usage

1. **Upload an Image**: Click the upload button to select a starting image
2. **Enter a Prompt**: Describe the motion you want (e.g., "The person dances gracefully")
3. **Select a Preset**: Choose a preset that matches your desired motion type
4. **Click Generate**: Press the "Start Generation" button

## Advanced Features

### Preset Configurations

Different presets are optimized for specific types of motion:

- **Default**: Balanced settings for general use
- **Dance**: Optimized for dance movements 
- **Talking**: Best for facial expressions and talking
- **Action**: Enhanced for dynamic movements
- **Subtle Movement**: For minimal, gradual movements
- **Hand Movement**: Specialized for detailed hand gestures

### Flow Shift Optimization

Flow Shift parameters control how the diffusion sampling process unfolds over time. Each preset uses optimized flow shift parameters for its specific motion type. You can also select Flow Shift presets manually in Advanced Settings:

- **standard**: Balanced default settings
- **dance**: Slightly reduced aggressiveness for dance movements
- **talking**: Less aggressive for facial movements
- **action**: Slightly more aggressive for dynamic motion
- **subtle**: Much less aggressive for subtle movements
- **hand_detail**: Significantly less aggressive for hand details

### Performance Settings

- **TeaCache**: Enable for 1.5-2x faster generation (may affect detail quality)
- **Hand Optimization**: Enable when using TeaCache to preserve hand/finger details
- **GPU Memory Preservation**: Increase if you encounter out-of-memory errors

## Tips for Best Results

- **For hand details**: Use the "Hand Movement" preset or enable Hand Optimization
- **For talking faces**: Use the "Talking" preset
- **For dance motions**: Use the "Dance" preset
- **For longer videos**: Increase the "Total Video Length" setting
- **For higher quality**: Increase "Diffusion Steps" to 30-35 (will be slower)
- **For consistent results**: Use the same seed value for multiple generations

## Understanding the Process

The video is generated using inverted anti-drifting sampling, which means:

1. The ending frames are generated first, then earlier frames
2. You'll see the progress as sections are generated
3. Be patient for the beginning of the video to appear

## Common Issues

- If you see black video output, try setting MP4 Compression to 16
- If you encounter memory errors, increase GPU Memory Preservation
- If hand/finger details look poor, enable Hand Optimization or disable TeaCache

For more detailed information, please refer to the main [README.md](../README.md).
