from typing import List, Dict, Any
from src.backend.services.persistence.models_pnl import PaperTradePnL

class PerformanceMetrics:
    @staticmethod
    def compute(trades: List[PaperTradePnL]) -> Dict[str, Any]:
        if not trades:
            return {}

        wins = [t for t in trades if t.net_pnl_usd > 0]
        losses = [t for t in trades if t.net_pnl_usd <= 0]
        
        total_trades = len(trades)
        total_wins = len(wins)
        total_losses = len(losses)
        
        gross_profit = sum(t.net_pnl_usd for t in wins)
        gross_loss = abs(sum(t.net_pnl_usd for t in losses))

        win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else 999.0

        avg_win = round(gross_profit / total_wins, 2) if total_wins > 0 else 0
        avg_loss = round(gross_loss / total_losses, 2) if total_losses > 0 else 0

        return {
            "total_trades": total_trades,
            "win_rate_pct": round(win_rate, 2),
            "profit_factor": profit_factor,
            "gross_profit_usd": round(gross_profit, 2),
            "gross_loss_usd": round(gross_loss, 2),
            "avg_win_usd": avg_win,
            "avg_loss_usd": avg_loss
        }
