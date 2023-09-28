FROM ubuntu:20.04

ENV DEBIAN_FRONTEND="noninteractive"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Install Opencv
RUN pip3 install opencv-python-headless

# Install Paho mqtt
RUN pip3 install paho-mqtt

# Clean up
RUN apt-get autoremove -y && apt-get clean

# Set the working directory
WORKDIR /home

# Copy your application code to the container
# COPY . /home

# Run your application
# CMD ["python3", "blur_filter/blur_filter.py", "./imgs/src"]
