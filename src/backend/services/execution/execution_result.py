from dataclasses import dataclass
from typing import Optional

@dataclass
class ExecutionResult:
    """
    Padroniza o retorno de qualquer execução (Paper ou Real).
    """
    success: bool
    executed_price_spot: Optional[float]
    executed_price_futures: Optional[float]
    executed_size_usd: float
    fee_paid_usd: float = 0.0 # Preparado para V2
    message: str = ""