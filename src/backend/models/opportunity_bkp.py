import uuid
from datetime import datetime
from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional, List, Dict, Any

class Opportunity(BaseModel):
    """
    Modelo de dados UNIVERSAL (F1-F17).
    Versão Institucional: Campos padronizados e método de governança de estado.
    """
    # --- IDENTIDADE ---
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    symbol: str
    exchange_spot: str
    exchange_futures: str
    
    # --- PREÇOS E SPREADS (Core F1/F2) ---
    spot_price: float = 0.0
    futures_price: float = 0.0
    spread_pct: float = 0.0      # Spread Bruto
    spread_exec_pct: float = 0.0 # Spread Executável (após slippage estimado)
    spread_net_pct: float = 0.0  # Spread Líquido (após fees)
    spread_gross_pct: float = 0.0 # Alias para spread bruto (compatibilidade)
    
    # [FIX] Campos Financeiros Críticos
    spread_net_usd: float = 0.0
    spread_net_pct_before_funding: float = 0.0
    
    volume_24h_usd: float = 0.0

    # --- FEES (F8) ---
    fees_total_pct: float = 0.0
    fees_total_usd: float = 0.0
    fee_spot_pct: float = 0.1
    fee_futures_pct: float = 0.06
    fees_paid_usd: float = 0.0
    
    # [LEGADO] Mantido para compatibilidade com Frontend antigo
    total_fees_pct: float = 0.0 
    total_fees_usd: float = 0.0

    # --- FUNDING (F8.1) ---
    funding_rate_pct: float = 0.0
    funding_cost_pct: float = 0.0
    funding_cost_usd: float = 0.0
    funding_usd: float = 0.0 
    funding_impact_usd: float = 0.0 # [NOVO] Impacto financeiro direto do funding

    # --- PERSISTÊNCIA E COMPORTAMENTO (F4) ---
    persistence_minutes: float = 0.0
    volatility_pct: float = 0.0
    spread_std_pct: float = 0.0
    score_breakdown: Dict[str, Any] = Field(default_factory=dict)
    behavior_flags: List[str] = Field(default_factory=list)
    behavior_adjustment: Dict[str, Any] = Field(default_factory=dict)
    
    # --- ESTATÍSTICAS HISTÓRICAS ---
    spread_seen_count: int = 0
    spread_closed_count: int = 0
    spread_inverted_count: int = 0
    spread_success_rate: float = 0.0
    
    first_seen_timestamp: float = 0.0   
    last_seen_timestamp: float = 0.0    
    max_spread_seen: float = 0.0        
    min_spread_seen: float = 0.0        
    
    # --- LIQUIDEZ (F5) ---
    spot_liq_usd: float = 0.0
    futures_liq_usd: float = 0.0
    top_liquidity_usd: float = 0.0
    top_liquidity_avg: float = 0.0
    top_liquidity_volatility: float = 0.0
    top_liquidity_stability: float = 0.0
    liquidity_flags: List[str] = Field(default_factory=list)

    # --- EXECUÇÃO EM PROFUNDIDADE (F5.2) ---
    depth_exec_usd: float = 0.0
    depth_exec_levels: int = 0
    depth_avg_spread: float = 0.0
    depth_flags: List[str] = Field(default_factory=list)
    depth_slippage_pct: float = 0.0
    
    # --- CAPITAL & RISCO (F9/F10) ---
    order_recommend_usd: float = 0.0
    order_risk_level: str = "NORMAL"
    order_confidence: float = 0.0
    allocation_reason: str = ""
    allocation_capped: bool = False
    order_size_factor: float = 1.0

    # --- DECISÃO DE EXECUÇÃO ---
    execution_decision: str = "HOLD" # [NOVO] EXECUTE, PAPER, HOLD, SKIP

    # --- PAPER TRADING (F5.4/F5.5) ---
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
    
    # --- INTELIGÊNCIA & REGIME (F12-F14) ---
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

    # --- PLANOS (F15/F17) ---
    execution_plan: Dict[str, Any] = Field(default_factory=dict)
    exit_plan: Dict[str, Any] = Field(default_factory=dict)
    partial_rebalance_plan: Optional[Dict[str, Any]] = None
    
    # --- AUDITORIA PÓS-TRADE (F11) ---
    execution_quality_score: int = 0
    fill_ratio: float = 0.0
    execution_latency_ms: int = 0
    execution_status: str = "PENDING"
    filled_usd: float = 0.0 
    
    # --- GESTÃO DE POSIÇÃO ---
    current_position_usd: float = 0.0
    allocated_capital_usd: float = 0.0
    pnl_pct: float = 0.0
    holding_hours: float = 0.0

    # --- KILL SWITCH & GOVERNANÇA (F16) ---
    risk_decision: str = "PENDING"
    risk_reasons: List[str] = Field(default_factory=list)
    global_kill_active: bool = False
    global_kill_reason: Optional[str] = None
    
    # [NOVO] Motivo específico de descarte desta oportunidade
    kill_reason: Optional[str] = None 

    # --- CAMPOS TEMPORÁRIOS (PRIVADOS) ---
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

    # --- MÉTODO INSTITUCIONAL DE GOVERNANÇA ---
    def mark_killed(self, reason: str):
        """
        Marca a oportunidade como morta/descartada de forma consistente.
        Define status, motivo e garante que não será executada.
        """
        self.status = "KILLED"
        self.kill_reason = reason
        self.execution_decision = "SKIP"
        self.order_risk_level = "BLOCKED"
        self.order_recommend_usd = 0.0
        
        # Adiciona tag para rastreabilidade
        tag = f"KILLED:{reason.replace(' ', '_').upper()}"
        if tag not in self.tags:
            self.tags.append(tag)

    def to_dict(self):
        """
        Converte o objeto Pydantic para um dicionário Python puro (JSON-safe).
        """
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.timestamp(),
            "symbol": self.symbol,
            "exchange_spot": self.exchange_spot,
            "exchange_futures": self.exchange_futures,
            "price_spot": self.spot_price,
            "price_futures": self.futures_price,
            "spread_pct": round(self.spread_pct, 4),
            "spread_exec_pct": round(self.spread_exec_pct, 4),
            "spread_net_pct": round(self.spread_net_pct, 4),
            "funding_rate_pct": round(self.funding_rate_pct, 6),
            "volume_24h_usd": round(self.volume_24h_usd, 2),
            # NÃO aplicar fallback aqui.
            # "top_liquidity_usd" precisa refletir a liquidez do topo do livro (F5),
            # enquanto "volume_24h_usd" continua sendo o volume (F3). O frontend
            # usa "volume_24h_usd" para filtros de universo e pode exibir ambos.
            "top_liquidity_usd": round(self.top_liquidity_usd, 2),
            "liquidity_display_usd": round(max(self.top_liquidity_usd, self.volume_24h_usd), 2),
            "score": int(self.score),
            "score_regime_adjusted": int(self.score_regime_adjusted),
            "trust_score": int(self.trust_score),
            "market_regime": self.market_regime,
            "quality_level": self.quality_level,
            "status": self.status,
            "execution_decision": self.execution_decision, # [NOVO]
            "kill_reason": self.kill_reason,             # [NOVO]
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
            "tags": self.tags,
            "depth_flags": self.depth_flags
        }