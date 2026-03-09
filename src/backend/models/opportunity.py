import uuid
from datetime import datetime
from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional, List, Dict, Any

class Opportunity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    symbol: str
    exchange_spot: str
    exchange_futures: str
    
    spot_price: float = 0.0
    futures_price: float = 0.0
    
    # [CAMPOS DE TOPO DE BOOK]
    spot_top_book_usd: float = 0.0
    futures_top_book_usd: float = 0.0
    
    spot_bid_price: float = 0.0
    futures_ask_price: float = 0.0
    close_spread_pct: float = 0.0
    pnl_close_usd: float = 0.0

    spot_bid_liq_usd: float = 0.0
    futures_ask_liq_usd: float = 0.0
    spread_pct: float = 0.0
    spread_exec_pct: float = 0.0
    spread_net_pct: float = 0.0
    spread_gross_pct: float = 0.0
    spread_net_usd: float = 0.0
    spread_net_pct_before_funding: float = 0.0
    volume_24h_usd: float = 0.0

    fees_total_pct: float = 0.0
    fees_total_usd: float = 0.0
    fee_spot_pct: float = 0.1
    fee_futures_pct: float = 0.06
    fees_paid_usd: float = 0.0
    total_fees_pct: float = 0.0 
    total_fees_usd: float = 0.0

    funding_rate_pct: float = 0.0
    funding_cost_pct: float = 0.0
    funding_cost_usd: float = 0.0
    funding_usd: float = 0.0
    funding_impact_usd: float = 0.0

    # ================================
    # V113 - Frontend Depth/Funding
    # ================================

    # Funding (formato decimal para frontend)
    funding_rate: float = 0.0                 # decimal (ex: 0.0001 = 0.01%)
    funding_interval_hours: int = 8
    next_funding_at: Optional[float] = None   # unix timestamp (seconds)

    # Price Range (Spread Range)
    range_low: float = 0.0
    range_high: float = 0.0
    range_basis: str = "spread_exec_pct"
    range_pct: float = 0.0

    # Orderbook Fill Intelligence
    orders_to_fill_spot: int = 0
    orders_to_fill_fut: int = 0
    orders_to_fill_total: int = 0
    fill_status: str = "OK"

    # ================================
    # V114 - Sweep Execution / Faixa de Preço Real
    # ================================
    # Preços de execução (sweep) - Spot
    spot_px_start: float = 0.0
    spot_px_limit: float = 0.0

    # Preços de execução (sweep) - Futuros
    fut_px_start: float = 0.0
    fut_px_limit: float = 0.0

    # ================================
    # V114 - Capacity Configuration & Calculated Fields
    # ================================
    bankroll_usd: float = 2000.0
    hedge_pct: float = 50.0
    leg_budget_usd: float = 500.0

    entry_min_usd: float = 200.0
    entry_max_usd: float = 500.0
    cap_max_leg_usd: float = 0.0
    entry_leg_usd: float = 0.0
    capacity_pct: float = 0.0
    capacity_band: str = "RED"
    capacity_reason: str = "NO_DEPTH"

    # ================================
    # V114 - ROI / Profit
    # ================================
    roi_net_pct: float = 0.0
    profit_usd: float = 0.0
    roi_basis: str = "TOTAL"
    roi_top_book_pct: float = 0.0 # Opcional, para tooltip "Raio-X do ROI"
    slippage_impact_pct: float = 0.0 # Opcional, para tooltip "Raio-X do ROI"

    persistence_minutes: float = 0.0
    volatility_pct: float = 0.0
    spread_std_pct: float = 0.0
    score_breakdown: Dict[str, Any] = Field(default_factory=dict)
    behavior_flags: List[str] = Field(default_factory=list)
    behavior_adjustment: Dict[str, Any] = Field(default_factory=dict)
    
    spread_seen_count: int = 0
    spread_closed_count: int = 0
    spread_inverted_count: int = 0
    spread_success_rate: float = 0.0
    
    first_seen_timestamp: float = 0.0   
    last_seen_timestamp: float = 0.0    
    max_spread_seen: float = 0.0        
    min_spread_seen: float = 0.0        
    
    spot_liq_usd: float = 0.0
    futures_liq_usd: float = 0.0
    top_liquidity_usd: float = 0.0
    
    # [ANTI-CRASH] Campos necessários para o TopLiquidityState
    top_liquidity_avg: float = 0.0
    top_liquidity_volatility: float = 0.0
    top_liquidity_stability: float = 0.0
    
    liquidity_flags: List[str] = Field(default_factory=list)

    depth_exec_usd: float = 0.0
    depth_exec_levels: int = 0
    depth_avg_spread: float = 0.0
    depth_flags: List[str] = Field(default_factory=list)
    depth_slippage_pct: float = 0.0
    
    order_recommend_usd: float = 0.0
    order_risk_level: str = "NORMAL"
    order_confidence: float = 0.0
    allocation_reason: str = ""
    allocation_capped: bool = False
    order_size_factor: float = 1.0

    execution_decision: str = "HOLD"
    auto_eligible: bool = False

    exec_flags: List[str] = Field(default_factory=list)
    exec_slices: List[Dict] = Field(default_factory=list)
    exec_total_usd: float = 0.0      
    exec_avg_price_spot: float = 0.0
    exec_avg_price_fut: float = 0.0
    exec_final_spread: float = 0.0
    exec_efficiency: float = 0.0
    exec_abort_reason: str = "N/A"
    
    paper_status: str = "PENDING"
    paper_executed_usd: float = 0.0
    paper_pnl_usd: float = 0.0
    paper_pnl_pct: float = 0.0
    paper_fees_usd: float = 0.0
    paper_slippage_pct: float = 0.0
    slippage_actual: float = 0.0
    
    score: float = 0.0
    score_base: float = 0.0
    score_adaptive: float = 0.0
    score_regime_adjusted: float = 0.0
    score_adjustment_factor: float = 1.0
    
    trust_score: int = 50
    quality_level: str = "WATCH"
    status: str = "OBSERVATION_ONLY"
    tags: List[str] = Field(default_factory=list)
    
    market_regime: str = "NORMAL"
    market_regime_factors: Dict[str, Any] = Field(default_factory=dict)

    execution_plan: Dict[str, Any] = Field(default_factory=dict)
    exit_plan: Dict[str, Any] = Field(default_factory=dict)
    partial_rebalance_plan: Optional[Dict[str, Any]] = None
    
    execution_quality_score: int = 0
    fill_ratio: float = 0.0
    execution_latency_ms: int = 0
    execution_status: str = "PENDING"
    filled_usd: float = 0.0 
    
    current_position_usd: float = 0.0
    allocated_capital_usd: float = 0.0
    pnl_pct: float = 0.0
    holding_hours: float = 0.0

    risk_decision: str = "PENDING"
    risk_reasons: List[str] = Field(default_factory=list)
    global_kill_active: bool = False
    global_kill_reason: Optional[str] = None
    kill_reason: Optional[str] = None 

    _temp_spot_book: List = PrivateAttr(default_factory=list)
    _temp_fut_book: List = PrivateAttr(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    @property
    def uid(self) -> str:
        return self.id

    @uid.setter
    def uid(self, value: str):
        self.id = value

    def mark_killed(self, reason: str):
        self.status = "KILLED"
        self.kill_reason = reason
        self.execution_decision = "SKIP"
        self.order_risk_level = "BLOCKED"
        self.order_recommend_usd = 0.0
        tag = f"KILLED:{reason.replace(' ', '_').upper()}"
        if tag not in self.tags: self.tags.append(tag)

    def to_dict(self):
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.timestamp(),
            "symbol": self.symbol,
            "exchange_spot": self.exchange_spot,
            "exchange_futures": self.exchange_futures,
            "spot_price": self.spot_price,
            "futures_price": self.futures_price,
            "price_spot": self.spot_price,
            "price_futures": self.futures_price,
            "spread_pct": round(self.spread_pct, 4),
            "spread_exec_pct": round(self.spread_exec_pct, 4),
            "spread_net_pct": round(self.spread_net_pct, 4),
            "spot_bid_price": round(self.spot_bid_price, 8),
            "futures_ask_price": round(self.futures_ask_price, 8),
            "close_spread_pct": round(self.close_spread_pct, 4),
            "pnl_close_usd": round(self.pnl_close_usd, 4),
            
            # [CRÍTICO] Dados corretos para o Frontend
            "spot_top_book_usd": round(self.spot_top_book_usd, 2),
            "futures_top_book_usd": round(self.futures_top_book_usd, 2),
            "spot_liq_usd": round(self.spot_liq_usd, 2),
            "futures_liq_usd": round(self.futures_liq_usd, 2),
            
            "funding_rate_pct": round(self.funding_rate_pct, 6),

            # ================================
            # V113 - Funding Extended
            # ================================
            "funding_rate": round(self.funding_rate, 8),
            "funding_interval_hours": self.funding_interval_hours,
            "next_funding_at": self.next_funding_at,

            # ================================
            # V113 - Price Range
            # ================================
            "range_low": round(self.range_low, 6),
            "range_high": round(self.range_high, 6),
            "range_basis": self.range_basis,
            "range_pct": round(self.range_pct, 6),

            # ================================
            # V113 - Order Fill Depth
            # ================================
            "orders_to_fill_spot": self.orders_to_fill_spot,
            "orders_to_fill_fut": self.orders_to_fill_fut,
            "orders_to_fill_total": self.orders_to_fill_total,
            "fill_status": self.fill_status,

            # ================================
            # V114 - Sweep Execution / Faixa de Preço Real
            # ================================
            "spot_px_start": round(self.spot_px_start, 8),
            "spot_px_limit": round(self.spot_px_limit, 8),
            "fut_px_start": round(self.fut_px_start, 8),
            "fut_px_limit": round(self.fut_px_limit, 8),

            # ================================
            # V114 - Capacity Configuration
            # ================================
            "bankroll_usd": round(self.bankroll_usd, 2),
            "hedge_pct": round(self.hedge_pct, 2),
            "leg_budget_usd": round(self.leg_budget_usd, 2),
            "entry_min_usd": round(self.entry_min_usd, 2),
            "entry_max_usd": round(self.entry_max_usd, 2),
            "cap_max_leg_usd": round(self.cap_max_leg_usd, 2),
            "entry_leg_usd": round(self.entry_leg_usd, 2),
            "capacity_pct": round(self.capacity_pct, 4),
            "capacity_band": self.capacity_band,
            "capacity_reason": self.capacity_reason,

            # ================================
            # V114 - ROI / Profit
            # ================================
            "roi_net_pct": round(self.roi_net_pct, 4),
            "profit_usd": round(self.profit_usd, 2),
            "roi_basis": self.roi_basis,
            "roi_top_book_pct": round(self.roi_top_book_pct, 4),
            "slippage_impact_pct": round(self.slippage_impact_pct, 4),

            "volume_24h_usd": round(self.volume_24h_usd, 2),
            "top_liquidity_usd": round(self.top_liquidity_usd, 2),
            
            # [CRÍTICO] Dados para evitar crash do Pipeline
            "top_liquidity_avg": round(self.top_liquidity_avg, 2),
            
            "score": int(self.score),
            "score_regime_adjusted": int(self.score_regime_adjusted),
            "trust_score": int(self.trust_score),
            "market_regime": self.market_regime,
            "quality_level": self.quality_level,
            "status": self.status,
            "execution_decision": self.execution_decision, 
            "kill_reason": self.kill_reason,             
            "spread_seen_count": self.spread_seen_count,
            "spread_success_rate": self.spread_success_rate,
            "spread_inverted_count": self.spread_inverted_count,
            "persistence_minutes": self.persistence_minutes,
            "order_recommend_usd": round(self.order_recommend_usd, 2),
            "order_risk_level": self.order_risk_level,
            "allocation_reason": self.allocation_reason,
            "global_kill_active": self.global_kill_active,
            "exit_plan": self.exit_plan,
            "partial_rebalance_plan": self.partial_rebalance_plan,
            "paper_status": self.paper_status,
            "paper_pnl_pct": self.paper_pnl_pct,
            "paper_executed_usd": self.paper_executed_usd,
            "paper_slippage_pct": self.paper_slippage_pct,
            "auto_eligible": self.auto_eligible,
            "tags": self.tags,
            "depth_flags": self.depth_flags
        }
