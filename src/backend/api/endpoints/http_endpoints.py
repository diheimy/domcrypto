"""HTTP API endpoints.

Implements REST endpoints following BACKEND-SPEC.md specification.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import List

from src.backend.api.schemas import (
    HealthResponse,
    OpportunitiesResponse,
    OpportunityDetailResponse,
    UserSettingsSchema,
    UpdateSettingsRequest,
    PnLHistoryResponse,
    PipelineSnapshotsResponse,
    ErrorResponse,
)
from src.backend.domain.opportunity_dto import OpportunityItemV2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["v1"])


# =============================================================================
# HEALTH CHECK
# =============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API health status"
)
async def health_check():
    """Health check endpoint.

    Returns current status of the API and its services.
    """
    from src.backend.main import app_state

    services_status = {
        "pipeline": app_state.get("pipeline_ready", False),
        "database": app_state.get("db_ready", False),
        "websocket": app_state.get("ws_ready", False),
    }

    all_healthy = all(services_status.values())

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        timestamp=datetime.utcnow(),
        version="0.2.0",
        services=services_status
    )


# =============================================================================
# OPPORTUNITIES
# =============================================================================

@router.get(
    "/opportunities",
    response_model=OpportunitiesResponse,
    summary="List opportunities",
    description="Get current arbitrage opportunities"
)
async def list_opportunities(
    status: str = Query(default="all", description="Filter by status"),
    min_score: int = Query(default=0, ge=0, le=100, description="Minimum score"),
    min_spread: float = Query(default=0, ge=0, description="Minimum spread %"),
    limit: int = Query(default=100, ge=1, le=500, description="Max items to return")
):
    """List current arbitrage opportunities.

    - **status**: Filter by opportunity status (ACTIVE, READY, OBSERVATION_ONLY, KILLED)
    - **min_score**: Minimum score threshold (0-100)
    - **min_spread**: Minimum spread percentage
    - **limit**: Maximum number of items to return
    """
    from src.backend.main import app_state

    opportunities = app_state.get("opportunities", [])

    # Apply filters
    filtered = opportunities

    if status != "all":
        filtered = [o for o in filtered if o.status == status.upper()]

    filtered = [o for o in filtered if o.score >= min_score]
    filtered = [o for o in filtered if o.spread_net_pct >= min_spread]

    # Apply limit
    filtered = filtered[:limit]

    # Build meta
    meta = {
        "cycle_id": app_state.get("cycle_id", 0),
        "ts": int(datetime.utcnow().timestamp() * 1000),
        "counts": {
            "total": len(opportunities),
            "active": len([o for o in opportunities if o.status == "ACTIVE"]),
            "obs": len([o for o in opportunities if o.status == "OBSERVATION_ONLY"]),
            "killed": len([o for o in opportunities if o.status == "KILLED"]),
        },
        "pipeline_latency_ms": app_state.get("pipeline_latency_ms", 0),
    }

    return OpportunitiesResponse(
        items=filtered,
        meta=meta
    )


@router.get(
    "/opportunities/{opportunity_id}",
    response_model=OpportunityDetailResponse,
    summary="Get opportunity details",
    description="Get details of a specific opportunity"
)
async def get_opportunity(opportunity_id: str):
    """Get details of a specific opportunity by ID."""
    from src.backend.main import app_state

    opportunities = app_state.get("opportunities", [])

    for opp in opportunities:
        if opp.id == opportunity_id:
            return OpportunityDetailResponse(item=opp, exists=True)

    return OpportunityDetailResponse(
        item=OpportunityItemV2(
            id=opportunity_id,
            symbol="",
            pair="",
            exchange_spot="",
            exchange_futures="",
            is_cross_venue=False,
            price_spot=0,
            price_futures=0,
            spread_exec_pct=0,
            spread_net_pct=0,
        ),
        exists=False
    )


# =============================================================================
# USER SETTINGS
# =============================================================================

@router.get(
    "/settings",
    response_model=UserSettingsSchema,
    summary="Get user settings",
    description="Get current user settings"
)
async def get_settings():
    """Get current user settings."""
    from src.backend.main import app_state

    settings = app_state.get("settings", {})
    return UserSettingsSchema(**settings)


@router.put(
    "/settings",
    response_model=UserSettingsSchema,
    summary="Update user settings",
    description="Update user settings"
)
async def update_settings(request: UpdateSettingsRequest):
    """Update user settings.

    Only provided fields will be updated.
    """
    from src.backend.main import app_state

    current_settings = app_state.get("settings", {})

    # Update only provided fields
    update_data = request.model_dump(exclude_unset=True)
    current_settings.update(update_data)

    # Persist settings (in production, save to database)
    app_state["settings"] = current_settings

    return UserSettingsSchema(**current_settings)


# =============================================================================
# PnL HISTORY
# =============================================================================

@router.get(
    "/pnl",
    response_model=PnLHistoryResponse,
    summary="Get PnL history",
    description="Get trading PnL history"
)
async def get_pnl_history(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    status: str = Query(default="all", description="Filter by status (OPEN/CLOSED)")
):
    """Get PnL history.

    - **days**: Number of days to look back (1-365)
    - **status**: Filter by trade status
    """
    from src.backend.main import app_state

    # In production, fetch from database
    pnl_records = app_state.get("pnl_history", [])

    return PnLHistoryResponse(
        items=pnl_records,
        total=len(pnl_records),
        summary={
            "total_pnl_usd": sum(r.get("pnl_usd", 0) or 0 for r in pnl_records),
            "trades_count": len(pnl_records),
        }
    )


# =============================================================================
# PIPELINE SNAPSHOTS
# =============================================================================

@router.get(
    "/snapshots",
    response_model=PipelineSnapshotsResponse,
    summary="Get pipeline snapshots",
    description="Get historical pipeline snapshots"
)
async def get_pipeline_snapshots(
    limit: int = Query(default=50, ge=1, le=500, description="Max snapshots to return")
):
    """Get historical pipeline snapshots.

    Returns performance metrics and statistics from pipeline cycles.
    """
    from src.backend.main import app_state

    snapshots = app_state.get("snapshots", [])

    return PipelineSnapshotsResponse(
        items=snapshots[-limit:],
        total=len(snapshots)
    )


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@router.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    """Generic exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return ErrorResponse(
        error="internal_error",
        message=str(exc),
        code="500"
    )
