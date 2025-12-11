#!/bin/bash
# Initial database setup script for GCP

set -e

echo "=== Database Initialization ==="

# Configuration - UPDATE THESE VALUES
PROJECT_ID="axial-radius-337205"
INSTANCE_NAME="codingthunder"
REGION="us-central1"
DB_USER="root"
DB_PASS="your-db-password"
DB_NAME="codingthunder"

CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"

echo "This will create the database tables in Cloud SQL"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Build image if not exists
docker build -t blogapp:latest .

# Run container with CREATE_TABLES=True
docker run --rm \
  -e CREATE_TABLES=True \
  -e CLOUD_SQL_CONNECTION_NAME="${CLOUD_SQL_CONNECTION_NAME}" \
  -e DB_USER="${DB_USER}" \
  -e DB_PASS="${DB_PASS}" \
  -e DB_NAME="${DB_NAME}" \
  -v /cloudsql:/cloudsql \
  blogapp:latest \
  python __init__.py

echo ""
echo "=== Database tables created successfully ==="
