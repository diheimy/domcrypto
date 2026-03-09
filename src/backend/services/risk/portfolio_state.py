from collections import defaultdict
from datetime import datetime
import logging

logger = logging.getLogger("RiskState")

class PortfolioRiskState:
    def __init__(self, total_capital=50000.0):
        self.total_capital = total_capital
        # EXPOSIÇÃO VIVA (Não reseta diariamente)
        self.total_exposure_usd = 0.0
        self.exchange_exposure = defaultdict(float)
        self.asset_exposure = defaultdict(float)
        
        # MÉTRICAS DIÁRIAS (Resetam a cada 24h)
        self.daily_pnl = 0.0
        self.loss_streak = 0 
        self.last_reset = datetime.utcnow()

    def reset_daily(self):
        """Reinicia métricas de performance sem afetar a exposição viva."""
        self.daily_pnl = 0.0
        self.loss_streak = 0
        self.last_reset = datetime.utcnow()

    @property
    def mode(self):
        """Define o modo tático baseado na sequência de perdas reais."""
        return "DEFENSIVE" if self.loss_streak >= 2 else "NORMAL"