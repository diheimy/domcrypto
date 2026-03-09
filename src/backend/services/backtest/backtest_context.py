from src.backend.services.paper.paper_ledger import PaperLedger
from src.backend.services.history.trade_history_store import TradeHistoryStore

class BacktestContext:
    """
    Gerenciador de Contexto para Backtests.
    Responsável por isolar o estado da memória (RAM) antes de uma execução.
    """

    @staticmethod
    def reset():
        """
        Limpa completamente o Ledger (Trades Ativos) e a Store (Histórico),
        garantindo que o backtest comece do zero.
        """
        # Acesso direto às estruturas internas para limpeza hard reset
        PaperLedger._active_trades.clear()
        PaperLedger._history = []
        
        TradeHistoryStore.clear()
        
        print("🧹 Contexto de Backtest resetado com sucesso.")