# Deployment Guide

## Prerequisites

- Python 3.9 or higher
- Google Gemini API key
- 2GB+ RAM
- 5GB+ disk space

## Deployment Options

## 1. Local Development

### Setup
```bash
# Clone repository
git clone <repository-url>
cd ai_legal_assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your GEMINI_API_KEY
```

### Run
```bash
python -m app.main
```

Access at: http://localhost:8000

---

## 2. Docker Deployment

### Build and Run
```bash
# Build image
docker build -t legal-assistant .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your-key-here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --name legal-assistant \
  legal-assistant
```

### Using Docker Compose
```bash
# Set environment variable
export GEMINI_API_KEY=your-key-here

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Configuration

**Dockerfile**:
- Base: Python 3.9 slim
- Installs system + Python dependencies
- Exposes port 8000
- Creates data directories

**docker-compose.yml**:
- Sets up volumes for persistence
- Configures environment variables
- Enables auto-restart

---

## 3. Production Server (Linux)

### Using Systemd Service

Create `/etc/systemd/system/legal-assistant.service`:

```ini
[Unit]
Description=AI Legal Research Assistant
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/legal-assistant
Environment="PATH=/opt/legal-assistant/venv/bin"
EnvironmentFile=/opt/legal-assistant/.env
ExecStart=/opt/legal-assistant/venv/bin/gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/legal-assistant/access.log \
    --error-logfile /var/log/legal-assistant/error.log
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Setup
```bash
# Install application
sudo mkdir -p /opt/legal-assistant
sudo cp -r . /opt/legal-assistant/
cd /opt/legal-assistant

# Create virtual environment
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt

# Create log directory
sudo mkdir -p /var/log/legal-assistant
sudo chown www-data:www-data /var/log/legal-assistant

# Set permissions
sudo chown -R www-data:www-data /opt/legal-assistant

# Enable and start service
sudo systemctl enable legal-assistant
sudo systemctl start legal-assistant
sudo systemctl status legal-assistant
```

---

## 4. Nginx Reverse Proxy

### Configuration

Create `/etc/nginx/sites-available/legal-assistant`:

```nginx
upstream legal_assistant {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://legal_assistant;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static {
        alias /opt/legal-assistant/static;
        expires 30d;
    }
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/legal-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 5. Kubernetes Deployment

### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legal-assistant
  labels:
    app: legal-assistant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: legal-assistant
  template:
    metadata:
      labels:
        app: legal-assistant
    spec:
      containers:
      - name: legal-assistant
        image: legal-assistant:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: legal-assistant-secrets
              key: gemini-api-key
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: legal-assistant-data
      - name: logs
        persistentVolumeClaim:
          claimName: legal-assistant-logs
---
apiVersion: v1
kind: Service
metadata:
  name: legal-assistant-service
spec:
  selector:
    app: legal-assistant
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: legal-assistant-secrets
type: Opaque
stringData:
  gemini-api-key: your-gemini-api-key-here
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: legal-assistant-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: legal-assistant-logs
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### Deploy
```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl get services
```

---

## 6. Cloud Platform Deployments

### AWS (EC2 + RDS)

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t3.medium or larger
   - Security group: Allow ports 22, 80, 443, 8000

2. **Setup Application**
   ```bash
   ssh ubuntu@your-ec2-instance
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   # Follow "Production Server" steps above
   ```

3. **Optional: RDS for Database**
   - Use RDS PostgreSQL instead of SQLite
   - Update `QUERY_HISTORY_DB` in .env

### Azure (App Service)

1. **Create App Service**
   ```bash
   az webapp create \
     --name legal-assistant \
     --resource-group myResourceGroup \
     --plan myAppServicePlan \
     --runtime "PYTHON:3.9"
   ```

2. **Deploy**
   ```bash
   az webapp up --name legal-assistant
   ```

3. **Configure**
   ```bash
   az webapp config appsettings set \
     --name legal-assistant \
     --settings GEMINI_API_KEY=your-key
   ```

### Google Cloud (Cloud Run)

1. **Build Container**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/legal-assistant
   ```

2. **Deploy**
   ```bash
   gcloud run deploy legal-assistant \
     --image gcr.io/PROJECT_ID/legal-assistant \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GEMINI_API_KEY=your-key
   ```

---

## Environment Variables (Production)

```bash
# Required
GEMINI_API_KEY=your-key...

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database Paths
VECTOR_DB_PATH=/app/data/vector_db
QUERY_HISTORY_DB=/app/data/query_history.db
DOCUMENTS_PATH=/app/data/documents

# Performance
ENABLE_PERFORMANCE_LOGGING=true
LOG_LEVEL=WARNING  # Use WARNING or ERROR in production

# Search Configuration (tune as needed)
VECTOR_WEIGHT=0.7
KEYWORD_WEIGHT=0.3
TOP_K_RESULTS=5

# Security (if implemented)
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=https://your-domain.com
```

---

## Health Checks

### Endpoint
```bash
curl http://localhost:8000/api/v1/health
```

### Expected Response
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "vector_db_status": "connected",
  "documents_indexed": 42,
  "total_queries": 156
}
```

---

## Monitoring

### Application Logs
```bash
# Systemd service
sudo journalctl -u legal-assistant -f

# Docker
docker logs -f legal-assistant

# File
tail -f logs/app.log
```

### Metrics
```bash
curl http://localhost:8000/api/v1/metrics
curl http://localhost:8000/api/v1/stats
```

### Performance Monitoring

Consider adding:
- **New Relic**: Application performance monitoring
- **DataDog**: Infrastructure + application monitoring
- **Prometheus + Grafana**: Metrics and dashboards
- **Sentry**: Error tracking

---

## Backup Strategy

### Data to Backup
1. **Vector Database**: `data/vector_db/`
2. **Query History**: `data/query_history.db`
3. **Documents**: `data/documents/`
4. **Configuration**: `.env`

### Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backups/legal-assistant"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup databases and documents
tar -czf $BACKUP_DIR/data_$DATE.tar.gz data/

# Keep last 7 days
find $BACKUP_DIR -name "data_*.tar.gz" -mtime +7 -delete
```

### Cron Schedule
```cron
# Daily backup at 2 AM
0 2 * * * /opt/legal-assistant/backup.sh
```

---

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   # Kill process
   kill -9 <PID>
   ```

2. **Permission Denied**
   ```bash
   sudo chown -R $USER:$USER data/
   sudo chmod -R 755 data/
   ```

3. **Out of Memory**
   - Reduce number of workers
   - Add swap space
   - Upgrade server

4. **Slow Performance**
   - Check logs for slow queries
   - Reduce CHUNK_SIZE
   - Add caching layer
   - Monitor with `/api/v1/metrics`

---

## Security Checklist

- [ ] Environment variables secured
- [ ] HTTPS/TLS enabled
- [ ] Firewall configured
- [ ] API rate limiting enabled
- [ ] Authentication implemented
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Monitoring and alerting configured
- [ ] Logs rotated and retained
- [ ] Secrets stored securely (not in code)

---

## Support

For deployment issues:
1. Check logs: `logs/app.log`
2. Verify health: `/api/v1/health`
3. Review metrics: `/api/v1/metrics`
4. Test endpoints: `/docs`

---

**Deployment successful? Test with:**
```bash
python cli.py --url https://your-domain.com health
```
