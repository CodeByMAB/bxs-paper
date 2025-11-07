FROM python:3.11-slim

# Install system dependencies (including Node.js for frontend build)
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --timeout=300 --retries=5 \
        fastapi==0.104.1 \
        uvicorn[standard]==0.24.0 \
        pydantic==2.5.0 \
        python-dotenv==1.0.0 \
        requests==2.31.0 \
        httpx==0.25.2 && \
    pip install --no-cache-dir --timeout=300 --retries=5 \
        numpy==1.26.2 && \
    pip install --no-cache-dir --timeout=300 --retries=5 \
        pandas==2.1.3 && \
    pip install --no-cache-dir --timeout=300 --retries=5 \
        pytest==7.4.3 \
        pytest-asyncio==0.21.1 \
        ruff==0.1.6 \
        black==23.11.0

# Create data and results directories first
RUN mkdir -p data results

# Build frontend first
COPY code/app/frontend/ ./code/app/frontend/
WORKDIR /app/code/app/frontend
RUN npm install && npm run build
WORKDIR /app

# Copy application code
COPY code/ ./code/
# Copy schema to /app/schema.sql (not /app/data/ because volume mount will overwrite it)
COPY data/schema.sql ./schema.sql
COPY .env.example .env.example

# Verify schema file was copied
RUN ls -la /app/schema.sql || (echo "ERROR: schema.sql not found!" && exit 1)

# Make pipeline runner executable
RUN chmod +x code/pipeline_runner.py

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy Start9 scripts
COPY start9/check-web.sh /usr/local/bin/
COPY start9/check-metrics.sh /usr/local/bin/
COPY start9/properties.sh /usr/local/bin/
COPY start9/set-config.sh /usr/local/bin/
COPY start9/get-config.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/check-web.sh /usr/local/bin/check-metrics.sh /usr/local/bin/properties.sh /usr/local/bin/set-config.sh /usr/local/bin/get-config.sh

# curl already installed above

# Expose API port (default 8080 for Start9, can be overridden)
EXPOSE 8080

# Set default environment variables
ENV API_PORT=8080
ENV PIPELINE_INTERVAL_SECONDS=600
ENV DB_PATH=/app/data/bxs.sqlite

# Use entrypoint script
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

