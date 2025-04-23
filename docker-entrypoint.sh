#!/bin/bash
set -e

# Explicitly disable HF offline mode
export HF_HUB_OFFLINE=0
unset HF_HUB_OFFLINE

# Print environment for debugging
echo "Environment:"
echo "HF_HUB_OFFLINE: ${HF_HUB_OFFLINE:-not set}"
echo "TRANSFORMERS_OFFLINE: ${TRANSFORMERS_OFFLINE:-not set}"
echo "DIFFUSERS_OFFLINE: ${DIFFUSERS_OFFLINE:-not set}"
echo "HF_HOME: ${HF_HOME:-not set}"
echo "HF_TOKEN: ${HF_TOKEN:+set (value hidden)}"

# Run the provided command
exec "$@"
