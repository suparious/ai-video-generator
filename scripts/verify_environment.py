#!/usr/bin/env python
"""
Verify Python environment and dependencies.
This script checks if key dependencies are properly installed and accessible.
"""

import os
import sys
import site

def verify_environment():
    """Check if key dependencies are installed and accessible."""
    print("\n=== Python Environment Verification ===\n")
    
    # Print Python version and path
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")
    
    # Try to import key dependencies
    dependencies = [
        "gradio", 
        "torch", 
        "numpy", 
        "einops",
        "diffusers",
        "transformers",
        "safetensors",
        "PIL"
    ]
    
    print("\n--- Dependency Check ---")
    all_success = True
    
    for dep in dependencies:
        try:
            module = __import__(dep)
            version = getattr(module, "__version__", "unknown")
            print(f"✓ {dep} (version: {version}) - Successfully imported")
        except ImportError as e:
            print(f"✗ {dep} - Import failed: {e}")
            all_success = False
    
    # Print site-packages directories
    print("\n--- Site Packages Locations ---")
    site_packages = site.getsitepackages()
    for idx, path in enumerate(site_packages, 1):
        if os.path.exists(path):
            print(f"{idx}. {path} (exists)")
        else:
            print(f"{idx}. {path} (does not exist)")
    
    # Check specific paths
    print("\n--- Critical Paths Check ---")
    critical_paths = [
        "/app/venv/lib/python3.13/site-packages",
        "/app/venv/lib/python3/site-packages",
        "/app/venv/lib/site-packages",
        "/usr/local/lib/python3.13/site-packages"
    ]
    
    for path in critical_paths:
        if os.path.exists(path):
            print(f"✓ {path} exists")
            # List a few directories to confirm content
            try:
                contents = os.listdir(path)
                print(f"  Contains {len(contents)} items (showing first 5):")
                for item in contents[:5]:
                    print(f"  - {item}")
            except Exception as e:
                print(f"  Error listing directory: {e}")
        else:
            print(f"✗ {path} does not exist")
    
    # Summary
    print("\n--- Summary ---")
    if all_success:
        print("All dependencies were successfully imported.")
    else:
        print("Some dependencies could not be imported. See details above.")
    
    # PYTHONPATH environment variable
    print("\n--- PYTHONPATH Environment Variable ---")
    pythonpath = os.environ.get('PYTHONPATH', '')
    if pythonpath:
        print(f"PYTHONPATH is set to: {pythonpath}")
        paths = pythonpath.split(':')
        for idx, path in enumerate(paths, 1):
            if os.path.exists(path):
                print(f"{idx}. {path} (exists)")
            else:
                print(f"{idx}. {path} (does not exist)")
    else:
        print("PYTHONPATH is not set.")
    
    print("\n=== Verification Complete ===\n")

if __name__ == "__main__":
    verify_environment()
