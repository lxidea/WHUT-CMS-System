# Architecture Documentation

## System Overview

CMS-WHUT is a three-tier content management system designed to aggregate, manage, and display university news and information.

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend Layer                      │
│          (Next.js + React + TypeScript)                 │
│                    Port: 3000                           │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/REST API
                 │
┌────────────────▼────────────────────────────────────────┐
│                     Backend Layer                        │
│             (FastAPI + PostgreSQL)                      │
│                   Port: 8000                            │
└────────────────┬────────────────────────────────────────┘
                 │ Database Access
                 │
┌────────────────▼────────────────────────────────────────┐
│                    Storage Layer                         │
│   PostgreSQL (metadata) + Redis (cache)                │
│          Ports: 5432, 6379                              │
└─────────────────────────────────────────────────────────┘
                 ▲
                 │ Data Push
┌────────────────┴────────────────────────────────────────┐
│                   Spider Layer                           │
│        (Scrapy + Celery + Redis Queue)                 │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Frontend (Port 3000)

**Technology:** Next.js 14 with App Router, React 18, TypeScript

**Responsibilities:**
- Render user interface
- Display news articles
- Handle user interactions
- Provide search and filtering
- Generate RSS feeds (future)
- Email subscriptions (future)

**Key Files:**
- `src/app/page.tsx` - Home page
- `src/components/NewsList.tsx` - News display
- `src/lib/api.ts` - Backend API client

### 2. Backend API (Port 8000)

**Technology:** FastAPI, SQLAlchemy, Pydantic

**Responsibilities:**
- RESTful API endpoints
- Data validation
- Database operations
- Business logic
- Authentication (future)
- Rate limiting (future)

**API Endpoints:**
- `GET /api/health` - Health check
- `GET /api/news/` - List news (paginated)
- `GET /api/news/{id}` - Get single news
- `POST /api/news/` - Create news (spider only)
- `PATCH /api/news/{id}` - Update news
- `DELETE /api/news/{id}` - Delete news
- `GET /api/news/categories/list` - List categories

**Database Schema:**

```sql
Table: news
├── id (PK)
├── title
├── content
├── summary
├── source_url (unique)
├── source_name
├── published_at
├── author
├── images (JSON array)
├── attachments (JSON array)
├── category
├── tags (JSON array)
├── is_published
├── is_featured
├── view_count
├── content_hash (unique, for deduplication)
├── created_at
└── updated_at
```

### 3. Spider System

**Technology:** Scrapy, Celery, Redis

**Responsibilities:**
- Crawl university news websites
- Extract structured data
- Deduplicate content
- Push to backend API
- Schedule periodic crawls

**Components:**
- **Scrapy Spider:** Web scraping engine
- **Celery Worker:** Task execution
- **Celery Beat:** Periodic scheduler
- **Pipelines:**
  - `ContentHashPipeline` - Generate hash for deduplication
  - `BackendAPIPipeline` - Send to backend API

**Crawl Schedule:**
- Default: Every hour
- Configurable in `spider/tasks.py`

### 4. Storage Layer

**PostgreSQL:**
- Primary data store
- Stores news metadata
- ACID compliance
- Full-text search support

**Redis:**
- Celery message broker
- Task result backend
- API response caching (future)
- Session storage (future)

## Data Flow

### News Ingestion Flow

```
University Website
    │
    ▼
Scrapy Spider (crawl)
    │
    ▼
ContentHashPipeline (hash content)
    │
    ▼
BackendAPIPipeline (HTTP POST)
    │
    ▼
Backend API (validate)
    │
    ▼
PostgreSQL (store)
    │
    ▼
Frontend (display)
```

### User Request Flow

```
User Browser
    │
    ▼
Frontend (Next.js)
    │
    ▼
Backend API (FastAPI)
    │
    ▼
PostgreSQL (query)
    │
    ▼
Backend API (response)
    │
    ▼
Frontend (render)
    │
    ▼
User Browser
```

## Deployment Architecture

### Development (WSL2)

```
WSL2 Environment
├── Docker Compose
│   ├── postgres container
│   ├── redis container
│   ├── backend container
│   ├── frontend container
│   ├── spider container
│   ├── celery-worker container
│   └── celery-beat container
└── Local file system (~/projects/cms-whut)
```

### Production (Ubuntu Server)

```
Ubuntu Server 20.04
├── Docker Compose (same containers)
├── Nginx (reverse proxy, future)
├── SSL/TLS certificates (future)
└── DDNS service (for internet access)
```

## Security Considerations

### Current
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration

### Future Enhancements
- JWT authentication
- Rate limiting
- API key for spider
- HTTPS/TLS
- Content Security Policy
- XSS protection

## Performance Optimization

### Current
- Database connection pooling
- Scrapy AutoThrottle
- PostgreSQL indexing on:
  - `source_url`
  - `content_hash`
  - `category`
  - `published_at`

### Future Enhancements
- Redis caching for API responses
- Database read replicas
- CDN for static assets
- Image optimization
- Lazy loading

## Scalability

### Horizontal Scaling Options
- Multiple Celery workers
- Backend API replicas (stateless)
- Frontend SSG pre-rendering
- Database replication

### Resource Requirements

**Minimum (Development):**
- 2 CPU cores
- 4GB RAM
- 20GB storage

**Recommended (Production):**
- 4 CPU cores
- 8GB RAM
- 50GB+ storage
- SSD preferred

## Monitoring & Logging

### Current Logging
- Scrapy logs: Spider execution
- FastAPI logs: API requests
- Celery logs: Task execution

### Future Monitoring
- Prometheus metrics
- Grafana dashboards
- Error tracking (Sentry)
- Uptime monitoring

## Future Enhancements

1. **Authentication System**
   - User accounts
   - Admin panel
   - Role-based access control

2. **Subscription Service**
   - Email notifications
   - RSS feeds
   - Webhook integrations

3. **Advanced Search**
   - Elasticsearch integration
   - Full-text search
   - Faceted search

4. **Content Management**
   - Manual article creation
   - Rich text editor
   - Media library

5. **Analytics**
   - View statistics
   - Popular content tracking
   - User behavior analysis
