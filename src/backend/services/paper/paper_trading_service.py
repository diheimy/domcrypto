from datetime import datetime
import logging
from src.backend.models.paper_trade import PaperTrade
from src.backend.services.paper.paper_ledger import PaperLedger
from src.backend.services.risk.risk_engine import RiskEngine
from src.backend.services.risk.risk_profile import RiskProfile
from src.backend.services.execution.execution_engine import ExecutionEngine

logger = logging.getLogger("PaperTrading")

ESTIMATED_COST_PCT = 0.12

class PaperTradingService:
    """
    Gestor de Estratégia (Decision Layer).
    """
    
    ENTRY_MIN_SPREAD_NET = 0.40
    ENTRY_MIN_SCORE = 50
    EXIT_CONVERGENCE_TARGET = 0.20 
    EXIT_MAX_TIME = 1800

    @classmethod
    def get_current_time(cls, op=None) -> datetime:
        if op and hasattr(op, 'timestamp') and op.timestamp:
            return op.timestamp
        return datetime.utcnow()

    @classmethod
    def process_batch(cls, opportunities: list):
        for op in opportunities:
            active_trade = PaperLedger.get_active_trade(
                op.symbol, op.exchange_spot, op.exchange_futures
            )

            if active_trade:
                cls._update_trade_state(active_trade, op)
                if cls._check_exit_conditions(active_trade, op):
                    cls._execute_close_sequence(active_trade, op)
            else:
                should_enter, capital_usd = cls._check_entry_conditions(op)
                if should_enter:
                    cls._execute_open_sequence(op, capital_usd)

    @classmethod
    def _execute_open_sequence(cls, op, capital_usd):
        trade_intent = cls._create_trade_intent(op, capital_usd)
        result = ExecutionEngine.get().execute_entry(trade_intent)
        
        if result.success:
            trade_intent.entry_spot_price = result.executed_price_spot
            trade_intent.entry_futures_price = result.executed_price_futures
            trade_intent.status = "PAPER_OPEN"
            PaperLedger.open_trade(trade_intent)
        else:
            RiskEngine.process_exit(capital_usd, 0.0)

    @classmethod
    def _execute_close_sequence(cls, trade, op):
        trade.exit_spot_price = trade.current_spot_price
        trade.exit_futures_price = trade.current_futures_price
        
        result = ExecutionEngine.get().execute_exit(trade)
        
        if result.success:
            trade.status = "PAPER_CLOSED"
            trade.closed_at = cls.get_current_time(op)
            trade.exit_spot_price = result.executed_price_spot
            trade.exit_futures_price = result.executed_price_futures
            
            pnl_usd = trade.volume_usd * (trade.pnl_pct / 100.0)
            trade.pnl_usd = pnl_usd
            
            PaperLedger.close_trade(trade)
            RiskEngine.process_exit(trade.volume_usd, pnl_usd)

    @classmethod
    def _check_entry_conditions(cls, op) -> tuple[bool, float]:
        spread_net = float(getattr(op, 'spread_net_pct', 0.0) or 0.0)
        if spread_net == 0.0:
             spread_raw = float(getattr(op, 'spread_pct', 0.0) or 0.0)
             spread_net = spread_raw - ESTIMATED_COST_PCT

        score = float(getattr(op, 'score', 0.0) or 0.0)
        status = getattr(op, 'status', 'OBSERVED') or 'OBSERVED'
        
        if spread_net < cls.ENTRY_MIN_SPREAD_NET: return False, 0.0
        if score < cls.ENTRY_MIN_SCORE: return False, 0.0
        if "BLOCKED" in status: return False, 0.0
        
        allowed, reason, size_usd = RiskEngine.evaluate_entry(op)
        if not allowed: return False, 0.0
            
        return True, size_usd

    @classmethod
    def _create_trade_intent(cls, op, capital_usd: float) -> PaperTrade:
        spread_raw = float(getattr(op, 'spread_pct', 0.0) or 0.0)
        spread_net = float(getattr(op, 'spread_net_pct', 0.0) or 0.0)
        if spread_net == 0.0: spread_net = spread_raw - ESTIMATED_COST_PCT
        
        now = cls.get_current_time(op)

        return PaperTrade(
            symbol=op.symbol,
            exchange_spot=op.exchange_spot,
            exchange_futures=op.exchange_futures,
            entry_spot_price=float(op.spot_price or 0.0),
            entry_futures_price=float(op.futures_price or 0.0),
            entry_spread_pct=spread_net,
            volume_usd=capital_usd,
            status="PENDING_EXECUTION",
            opened_at=now,
            current_spot_price=float(op.spot_price or 0.0),
            current_futures_price=float(op.futures_price or 0.0),
            current_spread_pct=spread_net,
            max_spread_seen=spread_net,
            pnl_pct=0.0
        )

    @classmethod
    def _update_trade_state(cls, trade: PaperTrade, op):
        now = cls.get_current_time(op)
        if trade.opened_at and now < trade.opened_at: return 

        trade.current_spot_price = float(op.spot_price or 0.0)
        trade.current_futures_price = float(op.futures_price or 0.0)
        
        if trade.current_spot_price > 0:
            gross = ((trade.current_futures_price - trade.current_spot_price) / trade.current_spot_price) * 100
            trade.current_spread_pct = gross - ESTIMATED_COST_PCT
        
        trade.max_spread_seen = max(trade.max_spread_seen, trade.current_spread_pct)
        trade.pnl_pct = trade.entry_spread_pct - trade.current_spread_pct
        
        if trade.opened_at:
            delta = (now - trade.opened_at).total_seconds()
            trade.duration_seconds = int(max(0, delta))

    @classmethod
    def _check_exit_conditions(cls, trade: PaperTrade, op) -> bool:
        reason = None
        pnl = float(trade.pnl_pct or 0.0) # Ex: -2.5 (%)
        
        # CORREÇÃO CRÍTICA DE UNIDADE: Decimal -> Percentual
        # profile_stop vem como -0.05. Multiplicamos por 100 -> -5.0
        profile_stop = RiskProfile.get().stop_loss_limit_pct * 100 

        if pnl >= cls.EXIT_CONVERGENCE_TARGET:
            reason = "TAKE_PROFIT"
        elif pnl <= profile_stop: # Comparação Percentual vs Percentual
            reason = f"STOP_LOSS_RISK ({pnl:.2f}%)"
        elif trade.duration_seconds >= cls.EXIT_MAX_TIME:
            reason = "TIME_EXIT"

        if reason:
            trade.exit_reason = reason
            return True
        return False