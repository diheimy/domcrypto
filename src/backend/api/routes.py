"""API router aggregation.

Following BACKEND-SPEC.md specification.
WebSocket endpoint is defined in `app.main` to avoid route conflicts.
"""

from fastapi import APIRouter
from src.backend.api.endpoints.http_endpoints import router as v1_router

# Main API router
router = APIRouter()

# Include v1 endpoints
router.include_router(v1_router)


@router.get("/", tags=["root"])
async def api_root():
    """API root information."""
    return {
        "name": "DomCrypto API",
        "version": "0.2.0",
        "description": "Cryptocurrency arbitrage opportunities API",
        "docs": "/docs",
        "health": "/health",
        "v1_endpoints": {
            "opportunities": "/api/v1/opportunities",
            "settings": "/api/v1/settings",
            "pnl": "/api/v1/pnl",
            "snapshots": "/api/v1/snapshots",
        }
    }
