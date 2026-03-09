from typing import Dict, List, Optional
from src.backend.models.paper_trade import PaperTrade
from src.backend.services.history.trade_history_writer import TradeHistoryWriter

class PaperLedger:
    """
    Gerencia apenas os trades ATIVOS em memória RAM.
    """
    _active_trades: Dict[str, PaperTrade] = {}

    @staticmethod
    def make_key(symbol: str, spot_ex: str, fut_ex: str) -> str:
        """Chave composta para permitir arbitragem múltipla no mesmo par"""
        return f"{symbol}:{spot_ex}:{fut_ex}"

    @classmethod
    def get_active_trade(cls, symbol: str, spot_ex: str, fut_ex: str) -> Optional[PaperTrade]:
        key = cls.make_key(symbol, spot_ex, fut_ex)
        return cls._active_trades.get(key)

    @classmethod
    def open_trade(cls, trade: PaperTrade):
        key = cls.make_key(trade.symbol, trade.exchange_spot, trade.exchange_futures)
        cls._active_trades[key] = trade

    @classmethod
    def close_trade(cls, trade: PaperTrade):
        key = cls.make_key(trade.symbol, trade.exchange_spot, trade.exchange_futures)
        
        if key in cls._active_trades:
            # 1. Remove da memória ativa (Ledger Operacional)
            del cls._active_trades[key]
            
            # 2. Persiste no histórico (Ledger Analítico)
            TradeHistoryWriter.record(trade)

    @classmethod
    def get_stats(cls):
        return {
            "active_count": len(cls._active_trades)
        }