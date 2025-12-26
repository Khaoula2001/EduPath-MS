FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip first
RUN pip install --default-timeout=1000 --retries=10 --no-cache-dir --upgrade pip

# Install PyTorch CPU (largest dependency - cache this layer)
# Using specific version to ensure cache stability
RUN pip install --default-timeout=1000 --retries=10 --no-cache-dir \
    torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

# Copy ONLY requirements.txt first for better caching
COPY requirements.txt .

# Install other Python dependencies (will be cached if requirements.txt doesn't change)
RUN pip install --default-timeout=1000 --retries=10 --no-cache-dir -r requirements.txt

# Pre-download the BERT model (cache this layer too)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the application code (this changes frequently, so it's last)
COPY . .

EXPOSE 8003

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
