from .base_exit_model import ExitModel

class SpreadConvergenceExit(ExitModel):
    """
    Fecha a operacao quando o spread convergiu o suficiente (Take Profit).
    """

    def __init__(self, target_convergence_pct: float = 0.8):
        self.target = target_convergence_pct

    def evaluate(self, snapshot, now, current_spot_price, current_futures_price):
        entry_spread = snapshot.spread_pct
        current_spread = ((current_futures_price - current_spot_price) / current_spot_price) * 100

        if entry_spread <= 0:
            return False, "INVALID_ENTRY_SPREAD"

        convergence = (entry_spread - current_spread) / entry_spread

        if convergence >= self.target:
            return True, f"SPREAD_CONVERGED_{round(convergence*100,1)}%"

        return False, "HOLD_SPREAD_NOT_CONVERGED"
