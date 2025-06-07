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
    python3-full \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install the Python dependencies in the virtual environment
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# For production, we would copy the source code
# But for development, we'll mount it as a volume
# COPY src/ .

# Default command to run the CLI
#ENTRYPOINT ["/opt/venv/bin/python3"]
#CMD ["src/cli.py"]
