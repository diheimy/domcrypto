from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BacktestResult:
    """
    Objeto consolidado com os resultados de um backtest.
    """
    equity_report: Dict[str, Any]
    total_trades: int
    win_rate: float
    max_drawdown_pct: float
    final_capital: float
    total_roi_pct: float