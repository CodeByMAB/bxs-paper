FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY code/ ./code/
COPY data/schema.sql ./data/schema.sql
COPY .env.example .env.example

# Make pipeline runner executable
RUN chmod +x code/pipeline_runner.py

# Create data and results directories
RUN mkdir -p data results

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose API port
EXPOSE 9090

# Set default environment variables
ENV API_PORT=9090
ENV PIPELINE_INTERVAL_SECONDS=600
ENV DB_PATH=/app/data/bxs.sqlite

# Use entrypoint script
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

