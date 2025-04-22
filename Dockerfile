FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PYTHON_VERSION=3.13.3 \
    PATH="/usr/local/bin:$PATH"

# Install basic dependencies needed for Python compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    curl \
    wget \
    git \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.13.3 first, before any pip commands
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
    && tar -xf Python-${PYTHON_VERSION}.tgz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --enable-optimizations --prefix=/usr/local \
    && make -j$(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-${PYTHON_VERSION} Python-${PYTHON_VERSION}.tgz \
    && ln -sf /usr/local/bin/python3.13 /usr/local/bin/python3 \
    && ln -sf /usr/local/bin/python3.13 /usr/local/bin/python \
    && ln -sf /usr/local/bin/pip3.13 /usr/local/bin/pip3 \
    && ln -sf /usr/local/bin/pip3.13 /usr/local/bin/pip

# Verify Python version
RUN python --version && pip --version

# Install remaining system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libavutil-dev \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavfilter-dev \
    libswscale-dev \
    gfortran \
    libopenblas-dev \
    cmake \
    libxsimd-dev \
    llvm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Install basic Python setup tools
RUN pip install --no-cache-dir wheel setuptools packaging

# Install PyTorch with CUDA 12.8 support
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for persistent storage
RUN mkdir -p /app/outputs /app/hf_download

# Set HF_HOME environment variable
ENV HF_HOME=/app/hf_download

# Expose the default Gradio port
EXPOSE 7860

# Run the application
CMD ["python", "demo_gradio.py", "--server", "0.0.0.0", "--port", "7860"]
