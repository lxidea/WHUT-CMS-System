# CMS-WHUT Deployment Guide

This guide covers deploying the CMS-WHUT system in both development and production environments.

## System Requirements

- Docker 20.10+ and Docker Compose 2.0+
- 2GB+ RAM
- 10GB+ disk space
- Ubuntu 20.04+ / Debian 11+ (or compatible Linux distribution)

## Quick Start (Development)

### 1. Clone and Setup

```bash
git clone <your-repo-url> cms-whut
cd cms-whut
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 3. Start All Services

```bash
# Build and start all containers
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# (Optional) Create initial admin user
docker-compose exec backend python -c "from app.core.database import SessionLocal; from app.models.user import User; from app.core.security import get_password_hash; db = SessionLocal(); admin = User(username='admin', email='admin@cms-whut.local', hashed_password=get_password_hash('admin123'), is_active=True); db.add(admin); db.commit(); print('Admin user created')"
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. Production Configuration

```bash
# Create production environment file
cp .env.example .env.production

# Edit production settings
nano .env.production
```

**Important production changes in `.env.production`:**

```bash
# Change database password
POSTGRES_PASSWORD=<strong-password-here>

# Generate new secret key
SECRET_KEY=$(openssl rand -hex 32)

# Disable debug mode
DEBUG=false

# Set production API URL
NEXT_PUBLIC_API_URL=http://your-domain.com

# Configure CORS
ALLOWED_ORIGINS=http://your-domain.com,https://your-domain.com
```

### 3. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    restart: always
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - internal

  redis:
    restart: always
    networks:
      - internal

  backend:
    restart: always
    environment:
      DEBUG: "false"
      SECRET_KEY: ${SECRET_KEY}
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    networks:
      - internal
      - web

  celery-worker:
    restart: always
    networks:
      - internal

  celery-beat:
    restart: always
    networks:
      - internal

  frontend:
    restart: always
    environment:
      NODE_ENV: production
    command: npm run build && npm start
    networks:
      - web

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - web

networks:
  internal:
    driver: bridge
  web:
    driver: bridge

volumes:
  postgres_data:
```

### 4. Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # API endpoints
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 5. Deploy

```bash
# Load production environment
export $(cat .env.production | xargs)

# Build and start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Initialize database
docker-compose exec backend alembic upgrade head

# Check all services are running
docker-compose ps
```

## Service Management

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart backend

# View service logs
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

### Database Management

```bash
# Backup database
docker-compose exec postgres pg_dump -U cms_user cms_whut > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20251129.sql | docker-compose exec -T postgres psql -U cms_user cms_whut

# Access database shell
docker-compose exec postgres psql -U cms_user cms_whut
```

### Monitoring

```bash
# Check service status
docker-compose ps

# Monitor resource usage
docker stats

# View recent logs
docker-compose logs --tail=100 -f

# Check Celery tasks
docker-compose exec celery-worker celery -A tasks inspect active
docker-compose exec celery-worker celery -A tasks inspect scheduled
```

## Automatic Crawling

The spider automatically crawls news every hour. To adjust:

1. Edit `spider/tasks.py`
2. Modify the `beat_schedule` configuration
3. Restart celery-beat:

```bash
docker-compose restart celery-beat
```

## Troubleshooting

### Database Connection Issues

```bash
# Check postgres is healthy
docker-compose exec postgres pg_isready -U cms_user

# View postgres logs
docker-compose logs postgres
```

### Frontend Not Loading

```bash
# Rebuild frontend
docker-compose up -d --build frontend

# Check frontend logs
docker-compose logs frontend
```

### Spider Not Running

```bash
# Check celery services
docker-compose logs celery-worker
docker-compose logs celery-beat

# Manually trigger crawl
docker-compose exec celery-worker celery -A tasks call tasks.crawl_whut_news
```

### Port Conflicts

If ports 3000, 8000, 5432, or 6379 are already in use:

```bash
# Stop conflicting services
sudo lsof -i :8000
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
```

## Security Checklist

- [ ] Change default passwords in `.env`
- [ ] Generate new `SECRET_KEY`
- [ ] Set `DEBUG=false` in production
- [ ] Configure firewall (allow only 80, 443)
- [ ] Set up SSL/TLS certificates
- [ ] Regular database backups
- [ ] Update CORS allowed origins
- [ ] Keep Docker images updated

## Backup Strategy

### Automated Daily Backups

```bash
# Create backup script
cat > /opt/cms-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/var/backups/cms-whut
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U cms_user cms_whut | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /opt/cms-backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/cms-backup.sh") | crontab -
```

## Scaling

### Horizontal Scaling

To handle more traffic:

```yaml
# In docker-compose.yml
celery-worker:
  deploy:
    replicas: 3

backend:
  deploy:
    replicas: 2
```

### Performance Tuning

```bash
# Increase worker processes
docker-compose exec backend gunicorn -w 8

# Adjust Celery concurrency
docker-compose exec celery-worker celery -A tasks worker --concurrency=4
```

## Updates and Maintenance

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Update Dependencies

```bash
# Backend
docker-compose exec backend pip install -r requirements.txt --upgrade

# Frontend
docker-compose exec frontend npm update
```

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review this guide
- Check GitHub issues
