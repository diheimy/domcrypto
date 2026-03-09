"""API Schemas - Pydantic models for request/response validation.

Follows BACKEND-SPEC.md specification for API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime


# =============================================================================
# HEALTH CHECK
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    version: str
    services: Dict[str, bool] = Field(
        default_factory=dict,
        description="Status dos serviços internos"
    )


# =============================================================================
# OPPORTUNITIES
# =============================================================================

class OpportunityItemSchema(BaseModel):
    """Opportunity item schema."""
    # Identidade
    id: str
    symbol: str
    pair: str
    exchange_spot: str
    exchange_futures: str
    is_cross_venue: bool

    # Preços
    price_spot: float
    price_futures: float

    # Spread
    spread_exec_pct: float
    spread_net_pct: float

    # ROI e Capacidade
    roi_net_pct: float
    profit_usd: float
    capacity_pct: float
    capacity_band: Literal["GREEN", "YELLOW", "RED"]
    entry_leg_usd: float

    # Liquidez
    spot_top_book_usd: float
    futures_top_book_usd: float
    volume_24h_usd: float

    # Funding
    funding_rate: float
    funding_interval_hours: int
    next_funding_at: Optional[int]

    # Execução
    orders_to_fill_spot: int
    orders_to_fill_fut: int
    fill_status: str

    # Score e Status
    score: int
    trust_score: int
    quality_level: str
    status: Literal["ACTIVE", "READY", "OBSERVATION_ONLY", "KILLED", "DEGRADED"]
    execution_decision: str
    kill_reason: Optional[str]

    # Meta
    persistence_minutes: int
    tags: List[str]
    ts_created: int
    ts_updated: int

    model_config = ConfigDict(from_attributes=True)


class OpportunityMetaSchema(BaseModel):
    """Metadata for opportunities response."""
    cycle_id: int
    ts: int
    counts: Dict[str, int]
    pipeline_latency_ms: float


class OpportunitiesResponse(BaseModel):
    """Paginated opportunities response."""
    items: List[OpportunityItemSchema]
    meta: OpportunityMetaSchema


class OpportunityDetailResponse(BaseModel):
    """Single opportunity detail response."""
    item: OpportunityItemSchema
    exists: bool


# =============================================================================
# USER SETTINGS
# =============================================================================

class UserSettingsSchema(BaseModel):
    """User settings schema."""
    profile_name: str = "default"
    min_spread_pct: float = Field(default=0.5, ge=0)
    min_score: int = Field(default=50, ge=0, le=100)
    min_volume_usd: int = Field(default=100000, ge=0)
    min_persistence_min: int = Field(default=0, ge=0)
    bankroll_usd: float = Field(default=10000, ge=0)
    hedge_pct: float = Field(default=100, ge=0, le=100)
    entry_min_usd: float = Field(default=100, ge=0)
    entry_max_usd: float = Field(default=1000, ge=0)
    hide_blocked: bool = False
    allow_cross: bool = True
    allow_same: bool = True
    spots: List[str] = Field(default_factory=lambda: ["binance", "mexc", "bybit"])
    futures: List[str] = Field(default_factory=lambda: ["binance_futures", "mexc_futures"])
    blocked_coins: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UpdateSettingsRequest(BaseModel):
    """Request to update user settings."""
    profile_name: Optional[str] = None
    min_spread_pct: Optional[float] = Field(default=None, ge=0)
    min_score: Optional[int] = Field(default=None, ge=0, le=100)
    min_volume_usd: Optional[int] = Field(default=None, ge=0)
    min_persistence_min: Optional[int] = Field(default=None, ge=0)
    bankroll_usd: Optional[float] = Field(default=None, ge=0)
    hedge_pct: Optional[float] = Field(default=None, ge=0, le=100)
    entry_min_usd: Optional[float] = Field(default=None, ge=0)
    entry_max_usd: Optional[float] = Field(default=None, ge=0)
    hide_blocked: Optional[bool] = None
    allow_cross: Optional[bool] = None
    allow_same: Optional[bool] = None
    spots: Optional[List[str]] = None
    futures: Optional[List[str]] = None
    blocked_coins: Optional[List[str]] = None


# =============================================================================
# PnL HISTORY
# =============================================================================

class PnLRecordSchema(BaseModel):
    """PnL record schema."""
    id: int
    symbol: str
    exchange_spot: str
    exchange_futures: str
    entry_at: datetime
    exit_at: Optional[datetime]
    entry_spread: float
    exit_spread: Optional[float]
    capital_usd: float
    pnl_usd: Optional[float]
    pnl_pct: Optional[float]
    fees_usd: Optional[float]
    status: Literal["OPEN", "CLOSED"]
    meta: Optional[Dict[str, Any]]


class PnLHistoryResponse(BaseModel):
    """PnL history response."""
    items: List[PnLRecordSchema]
    total: int
    summary: Dict[str, Any]


# =============================================================================
# PIPELINE SNAPSHOTS
# =============================================================================

class PipelineSnapshotSchema(BaseModel):
    """Pipeline snapshot schema."""
    id: int
    cycle_id: int
    ts: datetime
    count_raw: int
    count_active: int
    count_obs: int
    count_killed: int
    top_spread: Optional[float]
    top_symbol: Optional[str]
    meta: Optional[Dict[str, Any]]


class PipelineSnapshotsResponse(BaseModel):
    """Pipeline snapshots response."""
    items: List[PipelineSnapshotSchema]
    total: int


# =============================================================================
# SSE PAYLOAD
# =============================================================================

class SSEPayloadSchema(BaseModel):
    """Server-Sent Events payload schema."""
    items: List[OpportunityItemSchema]
    meta: OpportunityMetaSchema

    class Config:
        json_encoders = {
            datetime: lambda v: v.timestamp()
        }


# =============================================================================
# ERROR RESPONSES
# =============================================================================

class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
