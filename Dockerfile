FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps (if any) and Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY . /app

# Create non-root user and set permissions
RUN useradd -m beaversec && chown -R beaversec:beaversec /app
USER beaversec

# Default entrypoint to CLI
ENTRYPOINT ["python", "-m", "beaversec.cli.commands"]

# Example: docker run --rm beaversec:latest list
