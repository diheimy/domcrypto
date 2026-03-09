from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TradeHistory:
    """
    Snapshot imutável de um trade finalizado.
    Base para auditoria e analytics.
    """
    id: str
    symbol: str
    
    # Identificação
    exchange_spot: str
    exchange_futures: str
    
    # Tempos
    opened_at: datetime
    closed_at: datetime
    duration_seconds: int
    
    # Preços e Spreads
    entry_spread_pct: float
    exit_spread_pct: float
    
    # Resultado
    pnl_pct: float      # Resultado percentual (Ex: 0.45 para 0.45%)
    pnl_usd: float      # Estimativa nominal (Redundante na V1, mas útil para logs)
    volume_usd: float   # Liquidez no momento da entrada
    
    # Metadados
    exit_reason: str    # Motivo: TAKE_PROFIT, STOP_LOSS, TIME_EXIT