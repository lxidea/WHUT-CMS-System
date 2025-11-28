# CMS-WHUT

Content Management System for Wuhan University of Technology - A comprehensive system for aggregating, managing, and displaying university news and information.

## Project Overview

This CMS consists of three main components:

1. **Backend** - FastAPI-based REST API with PostgreSQL storage
2. **Spider** - Scrapy-based web scraper for fetching university news
3. **Frontend** - Next.js-based user interface for browsing and subscribing

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│  Database   │
│  (Next.js)  │      │  (FastAPI)   │      │(PostgreSQL) │
└─────────────┘      └──────────────┘      └─────────────┘
                            ▲
                            │
                     ┌──────┴───────┐
                     │    Spider    │
                     │   (Scrapy)   │
                     └──────────────┘
```

## Technology Stack

- **Backend**: Python 3.9+, FastAPI, PostgreSQL, Redis
- **Spider**: Python 3.9+, Scrapy, Celery
- **Frontend**: Node.js 18+, Next.js 14, React, TypeScript
- **Infrastructure**: Docker, Docker Compose
- **Storage**: PostgreSQL (metadata), MinIO/filesystem (files)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 18+

### Development Setup

1. Clone the repository
```bash
git clone <repository-url>
cd cms-whut
```

2. Start all services with Docker Compose
```bash
docker-compose up -d
```

3. Access the services:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
cms-whut/
├── backend/          # FastAPI application
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── spider/           # Scrapy project
│   ├── whut_spider/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # Next.js application
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docs/             # Documentation
├── docker-compose.yml
└── README.md
```

## Development

See individual component READMEs for detailed development instructions:
- [Backend Documentation](./backend/README.md)
- [Spider Documentation](./spider/README.md)
- [Frontend Documentation](./frontend/README.md)

## Deployment

For production deployment to Ubuntu server:
1. Ensure Docker and Docker Compose are installed
2. Configure environment variables
3. Run `docker-compose -f docker-compose.prod.yml up -d`

## License

Educational project for Wuhan University of Technology
