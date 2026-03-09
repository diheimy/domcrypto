from src.backend.services.risk.capital_state import CapitalState
from src.backend.services.risk.risk_profile import RiskProfile

class DrawdownGuard:
    """
    Circuit Breaker Financeiro.
    Impede novas operações se o sistema atingir o limite de perda.
    """

    @staticmethod
    def can_trade() -> tuple[bool, str]:
        state = CapitalState.get_snapshot()
        profile = RiskProfile.get()

        # Verifica Drawdown REALIZADO vs Limite
        # Ex: Atual -15% < Limite -10% -> BLOQUEIA
        if state.current_drawdown_pct < profile.max_drawdown_limit_pct:
            return False, f"MAX_DRAWDOWN_HIT ({state.current_drawdown_pct:.2f}%)"

        return True, "OK"