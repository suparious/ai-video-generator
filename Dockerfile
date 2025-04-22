FROM nvidia/cuda:12.8.0-devel-debian12

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

# Copy your wheels first if you have any
# The wheels directory should contain any custom compiled packages
# such as flash-attn, xformers, etc.
COPY --chown=root:root wheels/ /app/wheels/

# Copy the entire project
COPY --chown=root:root . /app/

# Create and activate virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install base Python packages
RUN pip install --upgrade pip && \
    pip install wheel setuptools packaging

# Install PyTorch with CUDA 12.8 (nightly build)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Install custom wheels if available
RUN if [ -d "/app/wheels" ] && [ "$(ls -A /app/wheels)" ]; then \
        pip install /app/wheels/*.whl; \
    fi

# Install other project requirements
RUN pip install -r requirements.txt

# fix potential bug with torch version
RUN pip uninstall torch torchvision torchaudio -y
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Create output directories
RUN mkdir -p /app/outputs /app/static /app/hf_download

# Set environment variables for CUDA
ENV PATH="/usr/local/cuda/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"

# Expose ports for Gradio
EXPOSE 7860

# Default command to run the application
ENTRYPOINT ["python", "demo_gradio.py", "--server", "0.0.0.0", "--port", "7860"]
