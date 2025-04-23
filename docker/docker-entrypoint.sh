#!/bin/bash
set -e

# ========== IMPORTANT: DISABLE ALL OFFLINE MODES ==========
# Force disable all HF offline mode environment variables
export HF_HUB_OFFLINE=0
export TRANSFORMERS_OFFLINE=0
export DIFFUSERS_OFFLINE=0

# These next lines are very important - they actually unset the variables
# which is different from setting them to 0
unset HF_HUB_OFFLINE

# ========== IMPORTANT: SET PYTHON ENVIRONMENT ==========
# Make sure Python can find installed packages
export PYTHONPATH="/app:/app/venv/lib/python3.13/site-packages:${PYTHONPATH}"

# Add any Python version-specific paths for systems with different Python versions
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
export PYTHONPATH="/app/venv/lib/python${PYTHON_VERSION}/site-packages:${PYTHONPATH}"

# Verify Python path and venv is properly set up
echo "Python version and environment:"
python --version
echo "Python path: $(which python)"
echo "Site packages: $(python -c "import site; print(site.getsitepackages())")"

# Print environment for debugging
echo "Environment after fixes:"
echo "HF_HUB_OFFLINE: ${HF_HUB_OFFLINE:-not set}"
echo "TRANSFORMERS_OFFLINE: ${TRANSFORMERS_OFFLINE:-not set}"
echo "DIFFUSERS_OFFLINE: ${DIFFUSERS_OFFLINE:-not set}"
echo "HF_HOME: ${HF_HOME:-not set}"
echo "HF_TOKEN: ${HF_TOKEN:+set (value hidden)}"

# Set up Python path at runtime
echo "Setting up Python path..."
python -c "import sys; sys.path.append('/app/scripts'); import setup_python_path"

# Verify environment (can be commented out once confirmed working)
echo "Verifying Python environment..."
python verify_environment.py

# Run the provided command with the correct Python path
echo "Running command: $@"
exec "$@"
