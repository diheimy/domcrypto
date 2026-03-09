from typing import List, Dict, Any

class DrawdownrenderDashboard:
    @staticmethod
    def analyze(equity_curve: List[Dict[str, Any]]) -> Dict[str, float]:
        if not equity_curve:
            return {"max_drawdown_pct": 0.0, "max_drawdown_usd": 0.0}

        peak_equity = -float("inf")
        max_dd_pct = 0.0
        max_dd_usd = 0.0

        for point in equity_curve:
            current_equity = point["equity"]
            if current_equity > peak_equity:
                peak_equity = current_equity
            
            dd_usd = peak_equity - current_equity
            dd_pct = (dd_usd / peak_equity * 100) if peak_equity > 0 else 0.0

            max_dd_usd = max(max_dd_usd, dd_usd)
            max_dd_pct = max(max_dd_pct, dd_pct)

        return {"max_drawdown_pct": round(max_dd_pct, 2), "max_drawdown_usd": round(max_dd_usd, 2)}
