# Start with the official Alpine Linux image
FROM alpine:latest

# Install required packages
RUN apk add --no-cache \
    build-base \
    cmake \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-dev \
    py3-pip \
    openblas-dev

# Install ONNX Runtime
RUN pip3 install --no-cache-dir onnxruntime

# Install OpenCV
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    g++ \
    make \
    cmake \
    linux-headers \
    musl-dev \
    python3-dev \
    py3-numpy-dev && \
    apk add --no-cache libjpeg-turbo-dev libpng-dev && \
    pip3 install --no-cache-dir opencv-python-headless && \
    apk del .build-deps

# Set the working directory
WORKDIR /app

# Copy your application code to the container
COPY . .

# Run your application
CMD ["python3", "your_app.py"]
