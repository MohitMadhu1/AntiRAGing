FROM python:3.12-slim

# Install system dependencies (needed for tree-sitter C extensions)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

RUN chmod +x start.sh

# Run the unified start script
CMD ["./start.sh"]
