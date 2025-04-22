# FramePack AI Video Generator - Troubleshooting Guide

This document provides solutions for common issues you might encounter when using the FramePack AI Video Generator.

## General Issues

### Application Won't Start

**Symptoms**: Error when running `python demo_gradio.py`

**Solutions**:
- Ensure you have installed all dependencies: `pip install -r requirements.txt`
- Check if you're using a supported GPU (NVIDIA RTX series)
- Verify that your CUDA installation is compatible with PyTorch
- Try installing PyTorch separately: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126`

### Out of Memory Errors

**Symptoms**: CUDA out of memory errors, application crashes

**Solutions**:
- Increase the GPU Memory Preservation value in the UI
- Reduce the resolution of your input image
- Close other applications using GPU memory
- Restart your computer to clear GPU memory

## Video Generation Issues

### Poor Hand/Finger Detail

**Symptoms**: Hands or fingers look distorted or unnatural

**Solutions**:
- Disable TeaCache completely for best quality
- Enable the "Hand Optimization" option when using TeaCache
- Use the "Hand Movement" preset which is optimized for hand details
- Select the "hand_detail" Flow Shift preset in Advanced Settings

### Video Looks Unnatural or Inconsistent

**Symptoms**: Strange motion, inconsistent movement

**Solutions**:
- Try different Flow Shift presets to find one that works best for your content
- For talking faces, use the "talking" Flow Shift preset
- For dance movements, use the "dance" Flow Shift preset
- For subtle movements, use the "subtle" Flow Shift preset
- Increase the Diffusion Steps to 30-35 for higher quality
- Adjust the Guidance Scale to control adherence to the prompt

### Black or Corrupted Video Output

**Symptoms**: Output video is black or corrupted

**Solutions**:
- Try changing the MP4 Compression value to 16
- Restart the application
- Check that your GPU drivers are up to date
- Try a different browser if using the web interface

### Beginning of Video Missing

**Symptoms**: The start of the video seems to be missing

**Solution**:
- This is expected behavior! The model uses inverted temporal order sampling, generating the ending first
- Be patient and wait for the full generation process to complete
- The beginning of the video will be generated in the final stages

## Flow Shift Specific Issues

### Flow Shift Presets Not Working

**Symptoms**: No visible difference when changing Flow Shift presets

**Solutions**:
- Ensure you're using a recent enough version of the application
- Check that flow_shift_configs.py is properly installed
- Try more extreme presets to see the difference more clearly
- Increase the Diffusion Steps to make differences more noticeable

### Flow-Related Error Messages

**Symptoms**: Errors about flow_preset, actual_flow_preset, or FLOW_SHIFT_CONFIGS

**Solutions**:
- Ensure config.py has the correct FLOW_SHIFT_CONFIGS dictionary
- Verify that the preset names match between config.py and flow_shift_configs.py
- Try using the default "standard" preset if you continue to have issues

### Custom Flow Shift Values

**Symptoms**: Need to fine-tune Flow Shift parameters beyond presets

**Solution**:
- Advanced users can modify flow_shift_configs.py to adjust mu and sigma values
- Smaller mu values create less aggressive flow shift (better for detail)
- Larger sigma values create smoother curves (better for subtle motion)
- Document your findings to help improve the preset system

## Performance Issues

### Slow Generation

**Symptoms**: Video generation is very slow

**Solutions**:
- Enable TeaCache for 1.5-2x speedup (may affect quality)
- Reduce the number of Diffusion Steps (25 is a good balance)
- Use a smaller resolution input image
- Close other GPU-intensive applications
- Consider using a more powerful GPU if available

### TeaCache Issues

**Symptoms**: TeaCache causing quality issues or not providing speedup

**Solutions**:
- For hand details, use TeaCache with Hand Optimization enabled
- If quality is critical, disable TeaCache completely
- Ensure you have enough GPU memory for TeaCache to work effectively
- Try different TeaCache thresholds by modifying TEACACHE_CONFIG in config.py

## Getting Help

If you continue to experience issues not covered in this guide:

1. Check the GitHub issues for similar problems
2. Make sure you're using the latest version of the software
3. Include detailed information when reporting issues:
   - Your GPU model and VRAM amount
   - Operating system details
   - Complete error messages
   - Steps to reproduce the issue
