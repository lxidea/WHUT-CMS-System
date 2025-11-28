from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import news, health

app = FastAPI(
    title="CMS-WHUT API",
    description="Content Management System for Wuhan University of Technology",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(news.router, prefix="/api/news", tags=["news"])

@app.get("/")
async def root():
    return {
        "message": "CMS-WHUT API",
        "version": "1.0.0",
        "docs": "/docs"
    }
