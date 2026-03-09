from src.backend.services.risk.capital_state import CapitalState
from src.backend.services.risk.risk_profile import RiskProfile

class PositionSizer:
    """
    Calculadora de tamanho de posição.
    """

    @staticmethod
    def calculate_size_usd(opportunity_score: float) -> float:
        state = CapitalState.get_snapshot()
        profile = RiskProfile.get()

        # 1. Base: % do Capital Total Realizado
        # Correção Semântica: pct vem como 20.0, então dividimos por 100
        allocation_ratio = profile.max_risk_per_trade_pct / 100.0
        base_size = state.current_capital * allocation_ratio

        # 2. Alocação fixa na V1
        size = base_size

        # 3. Validação: Capital Livre
        if size > state.free_capital:
            size = state.free_capital

        # 4. Tamanho Mínimo
        MIN_ORDER_SIZE = 10.0
        if size < MIN_ORDER_SIZE:
            return 0.0

        return round(size, 2)