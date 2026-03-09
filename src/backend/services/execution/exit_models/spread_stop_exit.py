from .base_exit_model import ExitModel

class SpreadStopExit(ExitModel):
    """
    Fecha se o spread piorar (aumentar) alem do limite seguro.
    """

    def __init__(self, max_adverse_pct: float = 0.5):
        self.max_adverse = max_adverse_pct

    def evaluate(self, snapshot, now, current_spot_price, current_futures_price):
        entry_spread = snapshot.spread_pct
        current_spread = ((current_futures_price - current_spot_price) / current_spot_price) * 100

        delta = current_spread - entry_spread

        if delta >= self.max_adverse:
            return True, f"STOP_SPREAD_WIDENED_{round(delta,3)}%"

        return False, "HOLD_WITHIN_RISK"
