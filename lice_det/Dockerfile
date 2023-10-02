FROM python:3.8-slim

ENV DEBIAN_FRONTEND="noninteractive"

# Install system dependencies
RUN apt-get update

# Install ONNX Runtime
RUN pip3 install onnxruntime

# Install Paho mqtt
RUN pip3 install paho-mqtt

# Install Opencv
RUN pip3 install opencv-python-headless

# Clean up
RUN apt-get autoremove -y && apt-get clean

# Set the working directory
WORKDIR /app

# Set mount to volume
RUN mkdir /data

# Copy your application code to the container
COPY . /app

# Run your application
CMD ["python3", "lice_det.py"]
