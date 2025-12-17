FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (gcc and g++ needed for some Python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script first
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copy application files
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data logs

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
