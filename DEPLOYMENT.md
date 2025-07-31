# Enhanced Information Validation Tool - Deployment Guide

## 🚀 Quick Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/rstamps01/ps-doc-analysis.git
cd ps-doc-analysis

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start the application
make build
make up

# Access the application
# Frontend: http://localhost
# Backend: http://localhost:5000
```

### Option 2: Manual Docker Build

```bash
# Build backend
docker build -t validation-tool-backend ./validation_tool

# Build frontend
docker build -t validation-tool-frontend ./validation-dashboard

# Run with Docker Compose
docker-compose up -d
```

## 🔧 Configuration Requirements

### 1. Google Cloud Setup

#### Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable APIs:
   - Google Sheets API
   - Google Drive API
4. Create service account:
   - IAM & Admin → Service Accounts
   - Create Service Account
   - Download JSON key file

#### Share Documents
Share your Google Sheets and Drive documents with the service account email address.

### 2. Environment Configuration

Create `.env` file from template:

```bash
cp .env.example .env
```

Key settings:

```bash
# Application
FLASK_ENV=production
PORT=5000

# Google APIs
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google-service-account.json

# Security
SECRET_KEY=your_secure_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Database
DATABASE_URL=sqlite:///data/validation_tool.db

# CORS
CORS_ORIGINS=*
```

### 3. Credentials Setup

Mount your Google service account JSON file:

```bash
# Create credentials directory
mkdir -p ./credentials

# Copy your service account JSON file
cp /path/to/your/service-account.json ./credentials/google-service-account.json
```

Update docker-compose.yml to mount credentials:

```yaml
services:
  backend:
    volumes:
      - ./credentials:/app/credentials:ro
```

## 🌐 Production Deployment

### AWS Deployment

#### Option 1: ECS (Elastic Container Service)

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push images
docker tag validation-tool-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/validation-tool-backend:latest
docker tag validation-tool-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/validation-tool-frontend:latest

docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/validation-tool-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/validation-tool-frontend:latest
```

#### Option 2: EC2 with Docker

```bash
# On EC2 instance
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy application
git clone https://github.com/rstamps01/ps-doc-analysis.git
cd ps-doc-analysis
# Configure .env and credentials
docker-compose up -d
```

### Google Cloud Platform

#### Cloud Run Deployment

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/validation-tool-backend ./validation_tool
gcloud builds submit --tag gcr.io/PROJECT-ID/validation-tool-frontend ./validation-dashboard

# Deploy to Cloud Run
gcloud run deploy validation-tool-backend \
  --image gcr.io/PROJECT-ID/validation-tool-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

gcloud run deploy validation-tool-frontend \
  --image gcr.io/PROJECT-ID/validation-tool-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
# Create resource group
az group create --name validation-tool-rg --location eastus

# Deploy containers
az container create \
  --resource-group validation-tool-rg \
  --name validation-tool-backend \
  --image validation-tool-backend:latest \
  --ports 5000 \
  --environment-variables FLASK_ENV=production

az container create \
  --resource-group validation-tool-rg \
  --name validation-tool-frontend \
  --image validation-tool-frontend:latest \
  --ports 80
```

## 🔒 Security Configuration

### SSL/TLS Setup

#### Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Traefik Configuration

```yaml
version: '3.8'
services:
  traefik:
    image: traefik:v2.9
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=your-email@example.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"

  frontend:
    build: ./validation-dashboard
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=myresolver"

  backend:
    build: ./validation_tool
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`your-domain.com`) && PathPrefix(`/api`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=myresolver"
```

## 📊 Monitoring & Logging

### Docker Compose with Monitoring

```yaml
version: '3.8'
services:
  # ... existing services ...

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

### Log Aggregation

```yaml
  fluentd:
    image: fluent/fluentd:v1.14-1
    volumes:
      - ./fluentd/conf:/fluentd/etc
      - /var/log:/var/log:ro
    ports:
      - "24224:24224"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Docker Permission Errors
```bash
sudo usermod -aG docker $USER
newgrp docker
```

#### 2. Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :5000
sudo lsof -i :80

# Stop conflicting services
sudo systemctl stop apache2
sudo systemctl stop nginx
```

#### 3. Google API Authentication
```bash
# Verify service account file
cat ./credentials/google-service-account.json | jq .

# Check file permissions
ls -la ./credentials/
```

#### 4. Build Failures
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

### Health Checks

```bash
# Check service status
make health

# View logs
make logs

# Test endpoints
curl http://localhost:5000/health
curl http://localhost/health
```

### Performance Tuning

#### Backend Optimization
```bash
# Increase worker processes
export WORKERS=4
export THREADS=2

# Optimize memory usage
export PYTHONOPTIMIZE=1
```

#### Frontend Optimization
```bash
# Enable gzip compression in nginx.conf
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# Set cache headers
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 📈 Scaling

### Horizontal Scaling

```yaml
version: '3.8'
services:
  backend:
    build: ./validation_tool
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure

  frontend:
    build: ./validation-dashboard
    deploy:
      replicas: 2
```

### Load Balancing

```yaml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
```

## 🔄 Updates & Maintenance

### Rolling Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
make build
docker-compose up -d --force-recreate
```

### Backup Strategy

```bash
# Backup data
docker run --rm -v validation-tool_validation_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/data-$(date +%Y%m%d).tar.gz -C /data .

# Backup database
docker exec validation-tool-backend sqlite3 /app/data/validation_tool.db ".backup /app/data/backup.db"
```

---

**For additional support, check the main README.md or create an issue in the GitHub repository.**

