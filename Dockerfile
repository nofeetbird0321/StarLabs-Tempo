FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data logs

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh 2>/dev/null || true

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
