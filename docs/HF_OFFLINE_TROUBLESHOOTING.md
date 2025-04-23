# Troubleshooting HuggingFace Hub Offline Mode Issues

If you encounter errors related to HuggingFace Hub offline mode, such as:

```
HF login failed: Cannot reach https://huggingface.co/api/whoami-v2: offline mode is enabled. To disable it, please unset the `HF_HUB_OFFLINE` environment variable.
```

This document will help you resolve them.

## Common Causes

1. The `HF_HUB_OFFLINE` environment variable is set to `1` somewhere in your environment
2. The Docker container has offline mode enabled by default for build performance
3. Environment variables not properly propagated between build and runtime stages

## Solutions

### 1. Check Current Environment Setup

You can verify the current state of your environment variables by running a one-off command in your container:

```bash
docker compose exec ai-video-generator env | grep HF
```

This will show you all environment variables containing "HF" and their values.

### 2. Update Your docker-compose.yml

Ensure your docker-compose.yml explicitly sets HF_HUB_OFFLINE to 0:

```yaml
environment:
  - HF_HOME=/app/hf_download
  - HF_TOKEN=${HF_TOKEN:-}
  - HF_HUB_OFFLINE=0
```

### 3. Rebuild Your Images

If you've made changes to environment variables, you need to rebuild your images:

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### 4. Update hf_login.py

The application includes error handling code in `diffusers_helper/hf_login.py` that detects and disables offline mode. If you're still experiencing issues, you can check this file to ensure it's correctly handling offline mode errors.

### 5. Manual Override

If all else fails, you can manually override the environment variable when starting the container:

```bash
docker compose down
HF_HUB_OFFLINE=0 docker compose up -d
```

## If Issues Persist

If you continue to experience offline mode issues after trying these solutions:

1. Check if any other environment variables related to offline mode are set:
   - `TRANSFORMERS_OFFLINE`
   - `DIFFUSERS_OFFLINE`

2. Consult the HuggingFace Hub documentation for additional troubleshooting steps.

3. Review Docker logs for any related errors:
   ```bash
   docker compose logs ai-video-generator
   ```
