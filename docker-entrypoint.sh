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

# Print environment for debugging
echo "Environment after fixes:"
echo "HF_HUB_OFFLINE: ${HF_HUB_OFFLINE:-not set}"
echo "TRANSFORMERS_OFFLINE: ${TRANSFORMERS_OFFLINE:-not set}"
echo "DIFFUSERS_OFFLINE: ${DIFFUSERS_OFFLINE:-not set}"
echo "HF_HOME: ${HF_HOME:-not set}"
echo "HF_TOKEN: ${HF_TOKEN:+set (value hidden)}"

# Run the provided command
exec "$@"
