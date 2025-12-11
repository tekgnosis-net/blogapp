#!/bin/bash
# GCP VM Deployment Script

set -e

echo "=== Blogapp GCP Deployment ==="

# Configuration - UPDATE THESE VALUES
PROJECT_ID="axial-radius-337205"
INSTANCE_NAME="codingthunder"
REGION="us-central1"
DB_USER="root"
DB_PASS="your-db-password"
DB_NAME="codingthunder"
PORT=8080

# Cloud SQL connection name format: PROJECT_ID:REGION:INSTANCE_NAME
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"

echo "Cloud SQL Connection: ${CLOUD_SQL_CONNECTION_NAME}"

# Pull latest code
echo "Pulling latest code from GitHub..."
git pull origin master

# Build Docker image
echo "Building Docker image..."
docker build -t blogapp:latest .

# Stop existing containers
echo "Stopping existing containers..."
docker stop blogapp-web 2>/dev/null || true
docker stop blogapp-db 2>/dev/null || true
docker rm blogapp-web 2>/dev/null || true
docker rm blogapp-db 2>/dev/null || true

# For GCP with Cloud SQL, we don't need the MySQL container
# Start the web application
echo "Starting web application..."
docker run -d \
  --name blogapp-web \
  -p ${PORT}:5000 \
  -e PORT=5000 \
  -e DEBUG=False \
  -e CLOUD_SQL_CONNECTION_NAME="${CLOUD_SQL_CONNECTION_NAME}" \
  -e DB_USER="${DB_USER}" \
  -e DB_PASS="${DB_PASS}" \
  -e DB_NAME="${DB_NAME}" \
  -v /cloudsql:/cloudsql \
  --restart unless-stopped \
  blogapp:latest

echo ""
echo "=== Deployment Complete ==="
echo "Application should be accessible at http://YOUR_VM_IP:${PORT}"
echo ""
echo "To view logs: docker logs -f blogapp-web"
echo "To restart: docker restart blogapp-web"
echo "To stop: docker stop blogapp-web"
