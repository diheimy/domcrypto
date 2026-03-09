from typing import Dict, Any
from src.backend.services.persistence.database import SessionLocal
from src.backend.services.persistence.models_pnl import PaperTradePnL
from .equity_curve_builder import EquityCurveBuilder
from .drawdown_analyzer import DrawdownAnalyzer
from .performance_metrics import PerformanceMetrics

class EquityReportService:
    @staticmethod
    def generate_report(initial_capital: float = 1000.0) -> Dict[str, Any]:
        session = SessionLocal()
        try:
            trades = session.query(PaperTradePnL).all()
            if not trades:
                return {"status": "no_data", "initial_capital": initial_capital, "metrics": {}}

            curve = EquityCurveBuilder.build(trades, initial_capital)
            dd_metrics = DrawdownAnalyzer.analyze(curve)
            perf_metrics = PerformanceMetrics.compute(trades)

            final_capital = curve[-1]["equity"] if curve else initial_capital
            total_return_pct = ((final_capital - initial_capital) / initial_capital) * 100

            return {
                "summary": {
                    "initial_capital": initial_capital,
                    "final_capital": final_capital,
                    "total_return_pct": round(total_return_pct, 2),
                    **dd_metrics
                },
                "metrics": perf_metrics,
                "equity_curve": curve
            }
        finally:
            session.close()
