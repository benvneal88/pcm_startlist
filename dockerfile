# Use the latest stable slim version of Debian
FROM python:3.9-slim

# Set the environment to non-interactive to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /PCMStartListApp

# Copy requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/

# Expose port
EXPOSE 5000

WORKDIR /PCMStartListApp/src

# Run the application
CMD ["python", "app.py"]
