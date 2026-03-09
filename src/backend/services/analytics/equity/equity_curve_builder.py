from typing import List, Dict, Any
from src.backend.services.persistence.models_pnl import PaperTradePnL

class EquityCurveBuilder:
    @staticmethod
    def build(trades: List[PaperTradePnL], initial_capital: float) -> List[Dict[str, Any]]:
        equity = initial_capital
        curve = []
        if trades:
            start_date = trades[0].timestamp_open
            curve.append({"timestamp": start_date, "equity": initial_capital, "pnl_change": 0.0})

        sorted_trades = sorted(trades, key=lambda t: t.timestamp_close)

        for trade in sorted_trades:
            equity += trade.net_pnl_usd
            curve.append({
                "timestamp": trade.timestamp_close,
                "equity": round(equity, 2),
                "pnl_change": trade.net_pnl_usd,
                "symbol": trade.symbol
            })
        return curve
