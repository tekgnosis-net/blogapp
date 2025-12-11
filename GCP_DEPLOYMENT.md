# GCP Deployment Guide

## Prerequisites

1. **GCP Compute Engine VM** with Docker installed
2. **Cloud SQL instance** (MySQL 8.0) - already have: `codingthunder`
3. **Cloud SQL Proxy** OR direct connection enabled
4. VM must have Cloud SQL Client role

## Setup Steps

### 1. Prepare Your VM

```bash
# SSH into your GCP VM
gcloud compute ssh YOUR_VM_NAME --zone=us-central1-a

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect

# Install Git (if not already installed)
sudo apt-get update
sudo apt-get install -y git
```

### 2. Clone Repository

```bash
cd ~
git clone https://github.com/tekgnosis-net/blogapp.git
cd blogapp
```

### 3. Configure Cloud SQL Connection

Edit `deploy-gcp.sh` and update these values:
- `PROJECT_ID`: Your GCP project ID (currently: axial-radius-337205)
- `INSTANCE_NAME`: Your Cloud SQL instance (currently: codingthunder)
- `REGION`: Your region (currently: us-central1)
- `DB_USER`: Database username (default: root)
- `DB_PASS`: Database password
- `DB_NAME`: Database name (currently: codingthunder)
- `PORT`: External port (default: 8080)

```bash
nano deploy-gcp.sh
# Update the configuration variables at the top
```

### 4. Set Up Cloud SQL Proxy (Recommended)

```bash
# Download Cloud SQL Proxy
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# Start Cloud SQL Proxy as a service
sudo mkdir -p /cloudsql
sudo ./cloud_sql_proxy -dir=/cloudsql -instances=axial-radius-337205:us-central1:codingthunder &
```

**Or** create a systemd service:

```bash
sudo tee /etc/systemd/system/cloud-sql-proxy.service > /dev/null <<EOF
[Unit]
Description=Cloud SQL Proxy
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/$USER
ExecStart=/home/$USER/cloud_sql_proxy -dir=/cloudsql -instances=axial-radius-337205:us-central1:codingthunder
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cloud-sql-proxy
sudo systemctl start cloud-sql-proxy
sudo systemctl status cloud-sql-proxy
```

### 5. Initialize Database (First Time Only)

```bash
# Update init-db-gcp.sh with your database credentials
nano init-db-gcp.sh

# Make scripts executable
chmod +x deploy-gcp.sh init-db-gcp.sh

# Create database tables
./init-db-gcp.sh
```

### 6. Deploy Application

```bash
# Deploy the application
./deploy-gcp.sh
```

### 7. Configure Firewall

```bash
# Allow traffic on port 8080
gcloud compute firewall-rules create allow-blogapp \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow blogapp traffic"
```

### 8. Access Your Application

Your app will be accessible at: `http://YOUR_VM_EXTERNAL_IP:8080`

## Environment Variables Reference

The application supports these environment variables:

- `DATABASE_URI`: Full database connection string (overrides all other DB settings)
- `CLOUD_SQL_CONNECTION_NAME`: Format `PROJECT_ID:REGION:INSTANCE_NAME`
- `DB_USER`: Database username
- `DB_PASS`: Database password
- `DB_NAME`: Database name
- `PORT`: Application port (default: 80, Docker uses 5000 internally)
- `DEBUG`: Enable debug mode (True/False, default: True)
- `CREATE_TABLES`: Create database tables on startup (True/False, default: False)

## Maintenance Commands

```bash
# View logs
docker logs -f blogapp-web

# Restart application
docker restart blogapp-web

# Stop application
docker stop blogapp-web

# Update and redeploy
cd ~/blogapp
git pull origin master
./deploy-gcp.sh

# Check Cloud SQL Proxy status
sudo systemctl status cloud-sql-proxy
```

## Troubleshooting

### Can't connect to database
1. Verify Cloud SQL Proxy is running: `sudo systemctl status cloud-sql-proxy`
2. Check socket exists: `ls -la /cloudsql/`
3. Verify instance connection name is correct
4. Check database credentials

### Container keeps restarting
```bash
docker logs blogapp-web
```

### Port already in use
```bash
# Check what's using the port
sudo lsof -i :8080

# Stop existing container
docker stop blogapp-web
docker rm blogapp-web
```

## Production Considerations

1. **Use Gunicorn**: The Dockerfile now includes Gunicorn. Update CMD to:
   ```dockerfile
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "__init__:app"]
   ```

2. **Use HTTPS**: Set up nginx reverse proxy with Let's Encrypt SSL

3. **Environment Variables**: Use GCP Secret Manager instead of hardcoded credentials

4. **Monitoring**: Set up GCP Cloud Monitoring and Logging

5. **Backups**: Enable automated Cloud SQL backups

6. **Scaling**: Consider using GCP Managed Instance Groups for auto-scaling
