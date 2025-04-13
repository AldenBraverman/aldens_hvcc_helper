# # >Rebuild and Reopen in Container
# FROM mcr.microsoft.com/devcontainers/base:jammy

# # RUN apt-get update && apt-get install -y gimp
# apt-get update && apt-get install -y gimp

# Use Ubuntu as the base image
FROM ubuntu:latest

# Set noninteractive mode to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Update package list and install dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    cmake \
    pkg-config \
    jq \

    # JUCE Linux Dependencies
    libasound2-dev \
    libjack-jackd2-dev \
    ladspa-sdk \
    libcurl4-openssl-dev  \
    libfreetype-dev libfontconfig1-dev \
    libx11-dev libxcomposite-dev libxcursor-dev libxext-dev libxinerama-dev libxrandr-dev libxrender-dev \
    libwebkit2gtk-4.1-dev \
    libglu1-mesa-dev \
    mesa-common-dev \

    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment in /venv
RUN python3 -m venv /venv

# Activate venv and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN /venv/bin/pip install --upgrade pip && /venv/bin/pip install -r /tmp/requirements.txt

# Set up environment variables to activate venv automatically
ENV PATH="/venv/bin:$PATH"

# ENV EXTERNAL_JUCE_LIB_PATH=/libs/juce

# Install emsdk
RUN git clone https://github.com/emscripten-core/emsdk.git /emsdk && \
    cd /emsdk && \
    git pull && \
    ./emsdk install latest && \
    ./emsdk activate latest

# Set up environment variables for emsdk
ENV PATH="/emsdk:/emsdk/upstream/emscripten:${PATH}"
ENV EMSDK="/emsdk"
ENV EMSDK_NODE="/emsdk/node/14.18.2_64bit/bin/node"
ENV EMSDK_PYTHON="/venv/bin/python"

# Source emsdk_env.sh automatically for shell sessions
RUN echo "source /emsdk/emsdk_env.sh" >> /root/.bashrc

COPY . ./

# Set the default command to bash
# CMD ["/bin/bash"]
CMD chmod 755 setup_env_with_hvcc.sh && ./setup_env_with_hvcc.sh


