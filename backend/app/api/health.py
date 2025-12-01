from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
import redis
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify all services are running
    """
    status = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown"
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"unhealthy: {str(e)}"
        status["status"] = "unhealthy"

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        status["redis"] = "healthy"
    except Exception as e:
        status["redis"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"

    return status
