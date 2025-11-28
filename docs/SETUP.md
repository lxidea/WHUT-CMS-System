# Setup Guide

Complete setup guide for CMS-WHUT development and deployment.

## Prerequisites

### Development Environment (WSL2/Linux)
- Docker & Docker Compose
- Python 3.9+
- Node.js 18+
- Git

### Production Server (Ubuntu 20.04)
- Docker & Docker Compose
- SSH access
- Domain/DDNS (optional, for internet access)

## Quick Start (Development)

### 1. Clone Repository

```bash
git clone https://github.com/lxidea/WHUT-CMS-System.git
cd WHUT-CMS-System
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Frontend (port 3000)
- Spider + Celery workers

### 4. Verify Services

```bash
# Check health
curl http://localhost:8000/api/health

# Check API docs
open http://localhost:8000/docs

# Check frontend
open http://localhost:3000
```

## Component-by-Component Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally (requires PostgreSQL and Redis)
uvicorn app.main:app --reload
```

### Spider Setup

```bash
cd spider

# Install dependencies
pip install -r requirements.txt

# Test spider
scrapy crawl whut_news

# Start Celery worker
celery -A tasks worker --loglevel=info

# Start Celery beat (scheduler)
celery -A tasks beat --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
npm run start
```

## Production Deployment

### On Your Ubuntu Server

1. **Install Docker:**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

2. **Clone Repository:**
```bash
git clone https://github.com/lxidea/WHUT-CMS-System.git
cd WHUT-CMS-System
```

3. **Configure for Production:**
```bash
cp .env.example .env
nano .env  # Update with production settings
```

4. **Start Services:**
```bash
docker-compose up -d
```

5. **Check Logs:**
```bash
docker-compose logs -f
```

### Setting up DDNS (Optional)

For exposing to internet:

1. Configure DDNS service (e.g., No-IP, DynDNS)
2. Set up Nginx reverse proxy with SSL
3. Configure firewall

Example Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.ddns.net;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## Customizing the Spider

**IMPORTANT:** The spider must be customized for your university's website.

1. Inspect your university's news page
2. Edit `spider/whut_spider/spiders/whut_news.py`
3. Update CSS selectors to match actual HTML structure
4. Test with: `scrapy crawl whut_news`

See [Spider README](../spider/README.md) for detailed instructions.

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres
```

### Spider Not Finding Content
- Verify CSS selectors using `scrapy shell <url>`
- Check if site requires JavaScript (may need Playwright)

### Frontend Can't Connect to Backend
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- Verify CORS settings in backend

### Port Conflicts
```bash
# Change ports in docker-compose.yml if needed
ports:
  - "8001:8000"  # Use different host port
```

## Maintenance

### Backup Database
```bash
docker-compose exec postgres pg_dump -U cms_user cms_whut > backup.sql
```

### Restore Database
```bash
docker-compose exec -T postgres psql -U cms_user cms_whut < backup.sql
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Update Code
```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```
