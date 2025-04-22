# FramePack AI Video Generator - Directory Structure

This document provides an overview of the repository structure to help you navigate the codebase.

## Main Files

- `demo_gradio.py` - Main application entry point with Gradio UI
- `config.py` - Central configuration file with presets and settings
- `requirements.txt` - Python package dependencies
- `README.md` - Main documentation
- `ROADMAP.md` - Development roadmap and future improvements
- `IMPROVEMENTS.md` - Documentation of implemented enhancements

## Documentation

- `docs/` - Documentation directory
  - `FLOW_SHIFT.md` - Documentation for flow shift parameter implementation
  - `DIRECTORY_STRUCTURE.md` - This file

## Core Implementation

- `diffusers_helper/` - Core implementation modules
  - `models/` - Neural network model implementations
    - `hunyuan_video_packed.py` - FramePack model implementation
  - `pipelines/` - Diffusion pipeline implementations
    - `k_diffusion_hunyuan.py` - Main diffusion sampling pipeline
    - `flow_shift_configs.py` - Flow shift parameter configurations
  - `k_diffusion/` - K-diffusion implementation
    - `uni_pc_fm.py` - UniPC sampler with flow matching
    - `wrapper.py` - Model wrapper for diffusion
  - `gradio/` - Gradio UI components
    - `progress_bar.py` - Original progress bar implementation
    - `enhanced_progress_bar.py` - Enhanced progress visualization
  - `hunyuan.py` - HunyuanVideo model utilities
  - `utils.py` - General utility functions
  - `memory.py` - Memory management utilities
  - `clip_vision.py` - CLIP vision model utilities
  - `bucket_tools.py` - Resolution bucketing utilities
  - `thread_utils.py` - Threading and async utilities
  - `hf_login.py` - HuggingFace login utility

## Outputs

- `outputs/` - Generated videos and images
- `static/` - Static assets
  - `custom.css` - Custom CSS styling

## Key Components and Features

### FramePack Implementation

The core FramePack implementation is in `diffusers_helper/models/hunyuan_video_packed.py`. It implements:
- Progressive input frame compression
- Context length management
- Various kernel sizes for compression

### Flow Shift Optimization

The flow shift parameter optimization is implemented in:
- `diffusers_helper/pipelines/flow_shift_configs.py` - Configuration and calculation
- `diffusers_helper/pipelines/k_diffusion_hunyuan.py` - Integration with the sampling process

### TeaCache Optimization

TeaCache optimization for speed and hand detail preservation is in:
- `config.py` - Configuration settings
- `diffusers_helper/models/hunyuan_video_packed.py` - Implementation

### User Interface

The Gradio UI is implemented in `demo_gradio.py` with components from:
- `diffusers_helper/gradio/` - UI components
- `static/custom.css` - Custom styling
