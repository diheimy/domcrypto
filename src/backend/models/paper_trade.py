from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

@dataclass
class PaperTrade:
    # Identificação
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    
    # Snapshot de Entrada (Imutável)
    exchange_spot: str = ""
    exchange_futures: str = ""
    entry_spot_price: float = 0.0
    entry_futures_price: float = 0.0
    entry_spread_pct: float = 0.0
    
    # Gestão de Posição
    volume_usd: float = 0.0
    opened_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "PAPER_OPEN" # PAPER_OPEN | PAPER_CLOSED
    
    # Dinâmica (Atualizado a cada tick)
    current_spot_price: float = 0.0
    current_futures_price: float = 0.0
    current_spread_pct: float = 0.0
    max_spread_seen: float = 0.0 # High Water Mark
    
    # Snapshot de Saída
    exit_spot_price: Optional[float] = None
    exit_futures_price: Optional[float] = None
    exit_spread_pct: Optional[float] = None
    closed_at: Optional[datetime] = None
    exit_reason: str = "" # TAKE_PROFIT | STOP_LOSS | EXPIRED | MARKET_CLOSE
    
    # Resultado
    pnl_usd: float = 0.0
    pnl_pct: float = 0.0
    duration_seconds: int = 0
