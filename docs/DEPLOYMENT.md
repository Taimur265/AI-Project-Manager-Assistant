# Deployment Guide

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- Nginx
- Domain name (optional but recommended)
- Anthropic API key

## Production Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE aipm_production;
CREATE USER aipm_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE aipm_production TO aipm_user;
\q
```

### 3. Backend Deployment

```bash
# Clone repository
git clone https://github.com/yourusername/ai-project-manager.git
cd ai-project-manager/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create production .env file
cat > .env << EOF
DATABASE_URL=postgresql://aipm_user:your_secure_password@localhost/aipm_production
ANTHROPIC_API_KEY=your_claude_api_key
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=False
EOF

# Run database migrations
alembic upgrade head
```

### 4. Create Systemd Service

```bash
sudo nano /etc/systemd/system/aipm-backend.service
```

Add this content:

```ini
[Unit]
Description=AI Project Manager Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/ai-project-manager/backend
Environment="PATH=/path/to/ai-project-manager/backend/venv/bin"
ExecStart=/path/to/ai-project-manager/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable aipm-backend
sudo systemctl start aipm-backend
sudo systemctl status aipm-backend
```

### 5. Frontend Deployment

```bash
cd ../frontend

# Install dependencies
npm install

# Create production .env
echo "NEXT_PUBLIC_API_URL=https://api.yourdomain.com" > .env.production

# Build for production
npm run build

# Install PM2 for process management
sudo npm install -g pm2

# Start Next.js with PM2
pm2 start npm --name "aipm-frontend" -- start
pm2 save
pm2 startup
```

### 6. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/aipm
```

Add this configuration:

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/aipm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificates
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Docker Deployment (Alternative)

### 1. Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

CMD ["npm", "start"]
```

### 3. Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: aipm_production
      POSTGRES_USER: aipm_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://aipm_user:${DB_PASSWORD}@db/aipm_production
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

Deploy with Docker Compose:

```bash
docker-compose up -d
```

## Monitoring and Maintenance

### Log Management

```bash
# View backend logs
sudo journalctl -u aipm-backend -f

# View frontend logs
pm2 logs aipm-frontend

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backups

Create a backup script:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/aipm"
mkdir -p $BACKUP_DIR

pg_dump -U aipm_user aipm_production > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

Add to crontab:

```bash
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

### Performance Tuning

**PostgreSQL:**

```bash
sudo nano /etc/postgresql/13/main/postgresql.conf
```

Adjust these settings:

```
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 16MB
```

**Nginx:**

```nginx
# Add to http block in /etc/nginx/nginx.conf
client_max_body_size 10M;
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

## Scaling Considerations

### Horizontal Scaling

- Use a load balancer (nginx, HAProxy) in front of multiple backend instances
- Implement Redis for session storage
- Use CDN for static frontend assets

### Database Scaling

- Set up read replicas for heavy read workloads
- Implement connection pooling with PgBouncer
- Consider managed database services (AWS RDS, Google Cloud SQL)

### Caching

Add Redis for caching:

```python
# backend/app/core/cache.py
import redis
from .config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)
```

## Security Best Practices

1. **Keep dependencies updated:**
   ```bash
   pip list --outdated
   npm outdated
   ```

2. **Use environment variables for secrets**
3. **Enable firewall:**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

4. **Regular security updates:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

5. **Monitor failed login attempts**
6. **Implement rate limiting**
7. **Regular backups**

## Troubleshooting

### Backend not starting

```bash
# Check logs
sudo journalctl -u aipm-backend -n 50

# Test manually
cd backend
source venv/bin/activate
python main.py
```

### Database connection issues

```bash
# Test connection
psql -U aipm_user -d aipm_production

# Check PostgreSQL status
sudo systemctl status postgresql
```

### Frontend not accessible

```bash
# Check PM2 status
pm2 status

# Restart frontend
pm2 restart aipm-frontend

# Check build output
cd frontend && npm run build
```
