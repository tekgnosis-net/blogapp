# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for MySQL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY blogapp/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY blogapp/ /app/

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (using 5000 instead of 80 to avoid requiring root)
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=__init__.py
ENV PYTHONUNBUFFERED=1

# Run the application with Gunicorn for production
# Can be overridden with docker run command for development
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "__init__:app"]
