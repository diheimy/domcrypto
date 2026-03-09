from datetime import datetime
from src.backend.models.paper_trade import PaperTrade
from src.backend.models.trade_history import TradeHistory
from src.backend.services.history.trade_history_store import TradeHistoryStore

class TradeHistoryWriter:
    """
    Serviço de gravação. Isola o Ledger (Memória Viva) 
    do Analytics (Memória Morta).
    """

    @staticmethod
    def record(trade: PaperTrade):
        # Define timestamp de fechamento se não houver
        closed_at = trade.closed_at or datetime.utcnow()
        
        # Calcula duração exata
        duration = 0
        if trade.opened_at:
            duration = int((closed_at - trade.opened_at).total_seconds())

        # Cria o objeto histórico (Mapping)
        history = TradeHistory(
            id=trade.id,
            symbol=trade.symbol,
            exchange_spot=trade.exchange_spot,
            exchange_futures=trade.exchange_futures,
            
            opened_at=trade.opened_at,
            closed_at=closed_at,
            duration_seconds=duration,
            
            entry_spread_pct=trade.entry_spread_pct,
            # Se saiu por time exit ou stop, o spread de saída é o atual
            exit_spread_pct=trade.exit_spread_pct if trade.exit_spread_pct is not None else trade.current_spread_pct,
            
            pnl_pct=trade.pnl_pct,
            pnl_usd=trade.pnl_usd,
            volume_usd=trade.volume_usd,
            
            exit_reason=trade.exit_reason or "UNKNOWN"
        )
        
        # Grava no Store
        TradeHistoryStore.add(history)