# Backend API

FastAPI-based REST API for CMS-WHUT content management system.

## Features

- RESTful API for news management
- PostgreSQL database with SQLAlchemy ORM
- Redis caching support
- Automatic API documentation (Swagger/OpenAPI)
- Health check endpoints
- CORS support for frontend integration

## Project Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   │   ├── health.py     # Health check endpoints
│   │   └── news.py       # News CRUD endpoints
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings management
│   │   └── database.py   # Database connection
│   ├── models/           # SQLAlchemy models
│   │   └── news.py       # News model
│   ├── schemas/          # Pydantic schemas
│   │   └── news.py       # News validation schemas
│   ├── services/         # Business logic (future)
│   └── main.py           # FastAPI application
├── Dockerfile
└── requirements.txt
```

## API Endpoints

### Health Check
- `GET /api/health` - Check service health

### News Management
- `GET /api/news/` - List news (paginated, filterable)
- `GET /api/news/{id}` - Get single news item
- `POST /api/news/` - Create news (spider endpoint)
- `PATCH /api/news/{id}` - Update news
- `DELETE /api/news/{id}` - Delete news
- `GET /api/news/categories/list` - Get all categories

### Query Parameters (GET /api/news/)
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `category`: Filter by category
- `search`: Full-text search in title/content
- `featured_only`: Show only featured news

## Development

### Local Setup (without Docker)

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
cp ../.env.example .env
# Edit .env with your configuration
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### With Docker Compose

From project root:
```bash
docker-compose up backend
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Testing

```bash
pytest
```

## Environment Variables

See `.env.example` in project root for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `DEBUG`: Enable debug mode
