# Stage 1: Build Python and dependencies
FROM nvidia/cuda:12.8.1-devel-ubuntu24.04 AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev curl git libncursesw5-dev \
    xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
    python3-full python3-pip python3-wheel python3-venv \
    libavutil-dev libavformat-dev libavcodec-dev libavdevice-dev \
    libavfilter-dev libswscale-dev gfortran libopenblas-dev \
    cmake libxsimd-dev llvm ffmpeg wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pyenv to handle Python 3.13.3
RUN curl https://pyenv.run | bash
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"

# Install Python 3.13.3 using pyenv
RUN pyenv install 3.13.3
RUN pyenv global 3.13.3

# Create app directory
WORKDIR /app

# Create and activate virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install base Python packages
RUN pip install --upgrade pip && \
    pip install wheel setuptools packaging

# Copy your wheels first if you have any
COPY wheels/ /app/wheels/

# Install PyTorch with CUDA 12.8
#RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Install custom wheels if available
RUN if [ -d "/app/wheels" ] && [ "$(ls -A /app/wheels)" ]; then \
        pip install /app/wheels/*.whl; \
    fi

# Copy just the requirements first to leverage Docker caching
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Fix potential bug with torch version
#RUN pip uninstall torch torchvision torchaudio -y && \
#    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
RUN pip uninstall torch torchvision torchaudio -y && \
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Clean up unnecessary files
RUN rm -rf $(pip cache dir) && \
    rm -rf /root/.cache/pip && \
    rm -rf /tmp/* && \
    rm -rf /root/.pyenv/sources/* && \
    rm -rf /root/.pyenv/cache/* && \
    find /root/.pyenv -name "*.o" -delete && \
    find /root/.pyenv -name "*.a" -delete

# Stage 2: Create the final runtime image
FROM nvidia/cuda:12.8.1-runtime-ubuntu24.04

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    python3-minimal \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Python and the virtual environment from the builder stage
COPY --from=builder /root/.pyenv /root/.pyenv
COPY --from=builder /app/venv /app/venv

# Set up Python environment
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="/root/.pyenv/bin:/root/.pyenv/shims:/app/venv/bin:$PATH"

# Don't attempt to download HF models in Docker build
ENV HF_HOME=/app/hf_download \
    TRANSFORMERS_OFFLINE=1 \
    DIFFUSERS_OFFLINE=1 \
    HF_HUB_OFFLINE=0 \
    PATH="/usr/local/cuda/bin:${PATH}" \
    LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"

# Set working directory
WORKDIR /app

# Copy application code (rely on .dockerignore to exclude large dirs)
COPY . /app/

# Create directories for volume mounts
RUN mkdir -p /app/outputs /app/hf_download /app/static

# Install HuggingFace Hub CLI
ENV HF_HUB_OFFLINE=0
RUN pip install huggingface_hub[cli]

# Expose port for Gradio
EXPOSE 7860

# Copy entrypoint script and make it executable
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Set entrypoint to ensure environment variables are properly set
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command to run the application
CMD ["python", "demo_gradio.py", "--server", "0.0.0.0", "--port", "7860"]
