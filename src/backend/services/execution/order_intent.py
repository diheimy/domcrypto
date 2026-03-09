from dataclasses import dataclass

@dataclass
class OrderIntent:
    """F7.1 - Intenção de Ordem Auditável"""
    symbol: str
    exchange: str
    side: str
    order_type: str
    price: float
    quantity: float
    notional_usd: float
    reduce_only: bool = False