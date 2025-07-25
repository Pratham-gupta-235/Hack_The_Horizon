# Adobe Combined Solution Dockerfile
# Supports both Challenge 1a and Challenge 1b

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data for Challenge 1b
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create directories
RUN mkdir -p /app/input /app/output /app/cache

# Copy source code
COPY src/ /app/src/
COPY config/ /app/config/
COPY main.py /app/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"]
