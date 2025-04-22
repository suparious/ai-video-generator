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

# Import after setting HF_HOME
try:
    from diffusers import AutoencoderKLHunyuanVideo
    from transformers import (
        LlamaModel, CLIPTextModel, LlamaTokenizerFast, CLIPTokenizer,
        SiglipImageProcessor, SiglipVisionModel
    )
except ImportError:
    print("Error: Required packages not installed. Please run:")
    print("pip install diffusers transformers")
    sys.exit(1)

print("Starting model downloads...")

# Download models - using same paths as in demo_gradio.py
models_to_download = [
    ("hunyuanvideo-community/HunyuanVideo", [
        ("tokenizer", LlamaTokenizerFast), 
        ("tokenizer_2", CLIPTokenizer),
        ("text_encoder", LlamaModel),
        ("text_encoder_2", CLIPTextModel),
        ("vae", AutoencoderKLHunyuanVideo)
    ]),
    ("Suparious/FLUX.1-Redux-dev-adaptor-bfl", [
        ("feature_extractor", SiglipImageProcessor),
        ("image_encoder", SiglipVisionModel)
    ]),
    ("Suparious/FP-image-to-video-FLUX.1-HV-bf16", [])
]

for model_name, components in models_to_download:
    print(f"\nDownloading {model_name}...")
    
    if not components:
        # For the transformer model, we just preload it without subfolder
        try:
            from diffusers_helper.models.hunyuan_video_packed import HunyuanVideoTransformer3DModelPacked
            # Use token if available
            if token:
                transformer = HunyuanVideoTransformer3DModelPacked.from_pretrained(
                    model_name, use_auth_token=token
                )
            else:
                transformer = HunyuanVideoTransformer3DModelPacked.from_pretrained(model_name)
            print(f"✓ Successfully downloaded {model_name}")
        except Exception as e:
            print(f"⚠ Error downloading {model_name}: {e}")
    else:
        for subfolder, model_class in components:
            try:
                # Use token if available
                if token:
                    model = model_class.from_pretrained(
                        model_name, subfolder=subfolder, use_auth_token=token
                    )
                else:
                    model = model_class.from_pretrained(model_name, subfolder=subfolder)
                print(f"✓ Successfully downloaded {model_name}/{subfolder}")
            except Exception as e:
                print(f"⚠ Error downloading {model_name}/{subfolder}: {e}")

print("\nAll models downloaded successfully!")
print("You can now run the Docker container with pre-downloaded models.")
