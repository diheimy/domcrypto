from typing import List
from src.backend.models.trade_history import TradeHistory

class TradeHistoryStore:
    """
    Fonte da verdade para histórico.
    Armazena a lista cronológica de trades fechados.
    """
    _db: List[TradeHistory] = []

    @classmethod
    def add(cls, trade: TradeHistory):
        cls._db.append(trade)

    @classmethod
    def get_all(cls) -> List[TradeHistory]:
        # Retorna cópia para evitar mutação acidental
        return list(cls._db)

    @classmethod
    def clear(cls):
        cls._db = []
        
    @classmethod
    def count(cls) -> int:
        return len(cls._db)