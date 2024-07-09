# Use the latest stable slim version of Debian
FROM debian:stable-slim

# Set the environment to non-interactive to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /src

# Copy requirements file
COPY src/requirements.txt .

# Install the Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src/ .

# # Specify the entrypoint for the container
# ENTRYPOINT ["python3"]
#
# # Specify the default command to run
# CMD ["app.py"]