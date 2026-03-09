from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from enum import Enum

# --- Definição do Enum (Onde estava o erro) ---
class StatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    READY = "READY"
    OBSERVATION_ONLY = "OBSERVAÇÃO"
    DEGRADED = "DEGRADADO"
    KILLED = "BLOQUEADO"

class VenueModeEnum(str, Enum):
    SAME = "same"
    CROSS = "cross"

class OpportunityScoreBreakdown(BaseModel):
    profit: float
    liquidity: float
    persistence: float
    risk: float

class OpportunitySchemaV1(BaseModel):
    id: str
    symbol: str
    pair: str
    base: str
    quote: str
    spot_exchange: str
    futures_exchange: str
    venue_mode: VenueModeEnum
    spot_ask: float
    spot_bid: float
    futures_bid: float
    futures_ask: float
    spread_pct: float
    spread_liq_pct: float
    fees_pct: float
    slippage_pct_est: float
    pnl_close_usd: float
    
    # Ticket A2 - Opcionais
    spot_top_book_usd: Optional[float] = Field(None, description="Best Ask * Size")
    futures_top_book_usd: Optional[float] = Field(None, description="Best Bid * Size")
    
    spot_liq_usd: float
    futures_liq_usd: float
    capacity_usd: float
    confidence: float = Field(..., ge=0.0, le=1.0)
    score: float
    score_breakdown: Optional[OpportunityScoreBreakdown] = None
    status: StatusEnum
    status_pt: str
    tags: List[str]

class MetaCounts(BaseModel):
    raw: int
    active: int
    obs: int = 0
    killed: int

class MetaTiming(BaseModel):
    build: int
    adapt: int = 0
    broadcast: int

class PayloadMeta(BaseModel):
    cycle: int
    counts: MetaCounts
    timing_ms: MetaTiming
    bytes: Optional[int] = 0
    exchanges: List[str]

class WebSocketPayloadV1(BaseModel):
    schema_version: Literal["opps.v1"] = "opps.v1"
    ts: int
    meta: PayloadMeta
    items: List[OpportunitySchemaV1] = []
