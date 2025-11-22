"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis

from app.config import settings
from app.core.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    System health check endpoint

    Returns:
        Health status of all services
    """
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {}
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "up"
    except Exception as e:
        health_status["services"]["database"] = "down"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        health_status["services"]["redis"] = "up"
    except Exception as e:
        health_status["services"]["redis"] = "down"
        health_status["status"] = "degraded"

    # Check AI service (just check if API key is configured)
    if settings.ANTHROPIC_API_KEY:
        health_status["services"]["ai_service"] = "configured"
    else:
        health_status["services"]["ai_service"] = "not_configured"
        health_status["status"] = "degraded"

    return health_status


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint
    """
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint
    """
    return {"alive": True}
