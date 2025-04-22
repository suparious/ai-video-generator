#!/usr/bin/env python
"""
Model pre-download script for FramePack AI Video Generator

This script downloads all required models to the local HF cache to ensure they're
available when running the Docker container. This avoids downloading models at runtime
and allows running the container in offline mode.
"""

import os
import sys
import argparse
from pathlib import Path

# Ensure we're using the correct HF_HOME
parser = argparse.ArgumentParser(description='Download models for Docker deployment')
parser.add_argument('--hf-home', type=str, default='./hf_download',
                    help='Path to Hugging Face cache directory')
parser.add_argument('--token', type=str,
                    help='Hugging Face token (defaults to HF_TOKEN environment variable if set)')
parser.add_argument('--validate-only', action='store_true',
                    help='Only validate that models exist in cache without loading them')
args = parser.parse_args()

# Set environment variables
os.environ['HF_HOME'] = os.path.abspath(args.hf_home)
print(f"Using HF_HOME: {os.environ['HF_HOME']}")

# Handle Hugging Face token
if args.token:
    os.environ['HF_TOKEN'] = args.token
    token = args.token
    print("Using HF_TOKEN from command line argument")
elif 'HF_TOKEN' in os.environ:
    token = os.environ['HF_TOKEN']
    print("Using HF_TOKEN from environment variable")
else:
    token = None
    print("No HF_TOKEN found. Downloads may be slower or rate-limited.")

# Create directories
Path(os.environ['HF_HOME']).mkdir(parents=True, exist_ok=True)

# Import libraries
try:
    import huggingface_hub
    from transformers.utils import cached_file
    from diffusers.utils import cached_file as diffusers_cached_file
except ImportError:
    print("Error: Required packages not installed. Please install according to README.md")
    sys.exit(1)

# Load the needed imports only if we're not just validating
if not args.validate_only:
    try:
        from diffusers import AutoencoderKLHunyuanVideo
        from transformers import (
            LlamaModel, CLIPTextModel, LlamaTokenizerFast, CLIPTokenizer,
            SiglipImageProcessor, SiglipVisionModel
        )
    except ImportError:
        print("Error: Required packages not installed. Please install according to README.md")
        sys.exit(1)

print("Starting model validation/download...")

# Model repository paths
models_to_validate = [
    "hunyuanvideo-community/HunyuanVideo",
    "Suparious/FLUX.1-Redux-dev-adaptor-bfl",
    "Suparious/FP-image-to-video-FLUX.1-HV-bf16"
]

# Function to validate/download model files without loading them into VRAM
def validate_or_download_model(repo_id, token=None):
    print(f"\nValidating/downloading {repo_id}...")
    try:
        # Check if the model exists by trying to get the model info
        # This will trigger a download if not in cache
        model_info = huggingface_hub.model_info(repo_id, token=token)
        print(f"✓ Model {repo_id} exists in hub")
        
        # Verify snapshots directory exists in cache
        repo_cache_path = huggingface_hub.snapshot_download(
            repo_id=repo_id, 
            token=token,
            local_files_only=args.validate_only  # Only use local files in validate mode
        )
        print(f"✓ Model files for {repo_id} {'verified in' if args.validate_only else 'downloaded to'} cache: {repo_cache_path}")
        return True
    except Exception as e:
        print(f"⚠ Error with {repo_id}: {e}")
        if args.validate_only:
            print(f"  The model may not be in your cache. Try running without --validate-only to download it.")
        return False

# Check each model
success = True
for model_path in models_to_validate:
    if not validate_or_download_model(model_path, token):
        success = False

if success:
    print("\nAll models successfully validated/downloaded!")
    print("You can now run the Docker container with these pre-downloaded models.")
else:
    print("\nSome models could not be validated or downloaded.")
    if args.validate_only:
        print("Try running without --validate-only to download missing models.")
    else:
        print("Check your internet connection and HF_TOKEN if provided.")
