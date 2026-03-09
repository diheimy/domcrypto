"""Domain DTOs for Opportunity data.

This module defines the canonical data transfer objects used throughout
the backend and sent to the frontend via WebSocket/SSE.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Literal, Optional


CapacityBand = Literal["GREEN", "YELLOW", "RED"]
OpStatus = Literal["ACTIVE", "READY", "OBSERVATION_ONLY", "KILLED", "DEGRADED"]


@dataclass
class OpportunityItemV2:
    """
    DTO OFICIAL (v2) - OpportunityItemV2

    Fonte da verdade entre Backend e Frontend.
    Segue especificação BACKEND-SPEC.md

    Atributos:
        id: Identificador único (ex: "BTC-binance-binance_futures")
        symbol: Símbolo do ativo (ex: "BTC")
        pair: Par de negociação (ex: "BTC/USDT")
        exchange_spot: Exchange do mercado spot
        exchange_futures: Exchange do mercado de futuros
        is_cross_venue: True se exchanges diferentes

        price_spot: Preço no mercado spot
        price_futures: Preço no mercado de futuros

        spread_exec_pct: Spread bruto para execução
        spread_net_pct: Spread líquido após fees

        roi_net_pct: ROI líquido percentual
        profit_usd: Lucro em USD
        capacity_pct: Capacidade de execução percentual
        capacity_band: Banda de capacidade (GREEN/YELLOW/RED)
        entry_leg_usd: Valor da perna de entrada em USD

        spot_top_book_usd: Liquidez no topo do book spot
        futures_top_book_usd: Liquidez no topo do book de futuros
        volume_24h_usd: Volume 24h em USD

        funding_rate: Funding rate atual
        funding_interval_hours: Intervalo do funding em horas
        next_funding_at: Timestamp do próximo funding

        orders_to_fill_spot: Ordens necessárias no spot
        orders_to_fill_fut: Ordens necessárias no futures
        fill_status: Status de preenchimento

        score: Score de qualidade (0-100)
        trust_score: Score de confiança (0-100)
        quality_level: Nível de qualidade
        status: Status da oportunidade
        execution_decision: Decisão de execução
        kill_reason: Motivo do kill (se aplicável)

        persistence_minutes: Tempo de persistência em minutos
        tags: Tags da oportunidade
        ts_created: Timestamp de criação
        ts_updated: Timestamp de atualização
    """

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
    roi_net_pct: float = 0.0
    profit_usd: float = 0.0
    capacity_pct: float = 0.0
    capacity_band: CapacityBand = "RED"
    entry_leg_usd: float = 0.0

    # Liquidez
    spot_top_book_usd: float = 0.0
    futures_top_book_usd: float = 0.0
    volume_24h_usd: float = 0.0

    # Funding
    funding_rate: float = 0.0
    funding_interval_hours: int = 8
    next_funding_at: Optional[int] = None

    # Execução
    orders_to_fill_spot: int = 0
    orders_to_fill_fut: int = 0
    fill_status: str = "PENDING"

    # Score e Status
    score: int = 0
    trust_score: int = 0
    quality_level: str = "LOW"
    status: OpStatus = "OBSERVATION_ONLY"
    execution_decision: str = "HOLD"
    kill_reason: Optional[str] = None

    # Meta
    persistence_minutes: int = 0
    tags: List[str] = field(default_factory=list)
    ts_created: int = 0
    ts_updated: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class OpportunityDTOv1:
    """
    DTO Legado (v1) - Mantido para compatibilidade.

    Deprecated: Usar OpportunityItemV2 para novos desenvolvimentos.
    """

    id: str
    symbol: str

    exchange_spot: str
    exchange_futures: str

    spot_price: float
    futures_price: float

    spread_pct: float
    spread_net_pct: float

    volume_24h_usd: float

    score: float
    health_score: float

    tags: List[str]

    # OBSERVED | PAPER_OPEN | PAPER_CLOSED | BLOCKED
    status: str

    timestamp: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
