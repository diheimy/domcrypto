import logging
from src.backend.services.risk.portfolio_state import PortfolioRiskState

logger = logging.getLogger("RiskManager")

class RiskManager:
    """
    Evaluates individual opportunities against portfolio limits and risk rules.
    """
    
    # Risk Limits
    MAX_POSITION_SIZE_USD = 500.0  # Max allocation per trade
    MIN_PROFIT_BUFFER = 0.05       # Minimum net spread to consider execution
    
    @staticmethod
    def evaluate(op, risk_state: PortfolioRiskState):
        """
        Analyzes an opportunity and determines the Execution Decision.
        Updates op.execution_decision and op.allocation_reason.
        """
        
        # 1. Blocked by Kill Switch?
        if op.status != "ACTIVE":
            op.execution_decision = "HOLD"
            # Reason is already set by GlobalKillEngine or Builder
            return op

        # 2. Check Net Spread
        if op.spread_net_pct < RiskManager.MIN_PROFIT_BUFFER:
            op.execution_decision = "HOLD"
            op.allocation_reason = f"Low Spread ({op.spread_net_pct:.2f}%)"
            op.order_risk_level = "HIGH"
            return op

        # 3. Check Portfolio Exposure (Mock implementation)
        # In a real system, we would check current holdings here.
        # current_exposure = risk_state.get_exposure(op.symbol)
        # if current_exposure > limit: ...

        # 4. Allocation Logic
        # Determine position size based on confidence/score
        allocation = RiskManager.MAX_POSITION_SIZE_USD
        
        # Adjust allocation based on score (if available)
        if op.score < 50:
            allocation *= 0.5  # Reduce size for lower quality scores
        
        # Liquidity Cap (Don't trade more than 10% of available liquidity)
        liq_cap = op.top_liquidity_usd * 0.10
        allocation = min(allocation, liq_cap)

        if allocation < 10.0: # Minimum trade size filter
            op.execution_decision = "HOLD"
            op.allocation_reason = "Alloc < $10"
            op.order_recommend_usd = 0.0
        else:
            op.execution_decision = "READY" # or "EXECUTE" depending on auto-trade setting
            op.allocation_reason = "Risk Check Passed"
            op.order_recommend_usd = round(allocation, 2)
            op.status = "READY" # Upgrade status for Frontend visibility

        return op