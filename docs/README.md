# FramePack AI Video Generator Documentation

This directory contains additional documentation for the FramePack AI Video Generator.

## Available Documentation

### Main Documents

- [Main README](../README.md) - Primary documentation with installation and usage instructions
- [ROADMAP](../ROADMAP.md) - Development roadmap with current status and future plans
- [IMPROVEMENTS](../IMPROVEMENTS.md) - Detailed list of enhancements implemented in the project

### Feature-Specific Documentation

- [FLOW_SHIFT.md](FLOW_SHIFT.md) - Documentation for the Flow Shift parameter implementation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide for getting up and running quickly
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Solutions for common issues and problems
- [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md) - Overview of the repository file structure

## Key Features

The FramePack AI Video Generator implements several key technologies from the paper [Packing Input Frame Context in Next-Frame Prediction Models for Video Generation](https://arxiv.org/abs/2504.12626):

1. **FramePack Architecture** - Compresses input frames based on their importance to maintain constant context length
2. **Anti-Drifting Sampling** - Uses inverted temporal order sampling to prevent quality degradation 
3. **Flow Shift Optimization** - Implements content-specific, balanced diffusion schedulers
4. **TeaCache** - Provides speed optimization with specialized settings for preserving detail

## Recent Updates

The most recent update includes:

- **Flow Shift Parameter Tuning**: Implementation of optimized flow shift parameters for different content types
- **Enhanced UI**: Improved user interface with preset configurations
- **Documentation**: Comprehensive documentation of all features

## Getting Help

If you need additional assistance:
- Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide
- Look through existing GitHub issues
- Reference the [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md) to find specific components
