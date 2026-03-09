from typing import List, Dict, Any
from src.backend.services.history.trade_history_store import TradeHistoryStore

class EquityCurveService:
    """
    Gera relatórios financeiros baseados no histórico de trades.
    """

    @staticmethod
    def generate_report(initial_capital: float = 1000.0) -> Dict[str, Any]:
        trades = TradeHistoryStore.get_all()
        
        current_equity = initial_capital
        equity_curve = []
        wins = 0
        
        # Snapshot Inicial (T0)
        equity_curve.append({
            "t": "Início",
            "equity": initial_capital,
            "pnl_trade": 0,
            "symbol": "-"
        })

        peak_equity = initial_capital
        max_drawdown_pct = 0.0

        for t in trades:
            # Cálculo de PnL Composto
            # Assume que o trade usou o capital total disponível (Simplificação V1)
            # Ex: pnl_pct 0.5% -> Multiplicador 0.005
            pnl_decimal = t.pnl_pct / 100.0
            
            profit_usd = current_equity * pnl_decimal
            current_equity += profit_usd

            # Estatísticas de Win Rate
            if t.pnl_pct > 0: wins += 1
            
            # Cálculo de Drawdown (Queda em relação ao topo histórico)
            if current_equity > peak_equity:
                peak_equity = current_equity
            
            if peak_equity > 0:
                dd = (current_equity - peak_equity) / peak_equity * 100
                if dd < max_drawdown_pct:
                    max_drawdown_pct = dd

            # Ponto na curva
            equity_curve.append({
                "t": t.closed_at.isoformat(),
                "equity": round(current_equity, 2),
                "symbol": t.symbol,
                "pnl_pct": round(t.pnl_pct, 4)
            })

        count = len(trades)
        win_rate = (wins / count * 100) if count > 0 else 0.0
        roi_total = ((current_equity - initial_capital) / initial_capital) * 100

        return {
            "initial_capital": initial_capital,
            "final_capital": round(current_equity, 2),
            "total_trades": count,
            "win_rate": round(win_rate, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "total_roi_pct": round(roi_total, 2),
            "equity_curve": equity_curve
        }