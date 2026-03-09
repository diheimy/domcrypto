from typing import Tuple
from src.backend.services.risk.capital_state import CapitalState
from src.backend.services.risk.risk_profile import RiskProfile
from src.backend.services.risk.position_sizer import PositionSizer
from src.backend.services.risk.exposure_manager import ExposureManager
from src.backend.services.risk.drawdown_guard import DrawdownGuard

class RiskEngine:
    """
    Fachada Única de Risco.
    Coordena verificação de saúde, exposição e alocação.
    """

    @staticmethod
    def evaluate_entry(opportunity) -> Tuple[bool, str, float]:
        """
        Avalia se um trade pode ser aberto.
        Retorna: (Allowed: bool, Reason: str, SizeUSD: float)
        """
        
        # 1. Circuit Breaker (Saúde Financeira)
        ok, reason = DrawdownGuard.can_trade()
        if not ok:
            return False, reason, 0.0

        # 2. Filtro de Exposição (Risco Sistêmico)
        ok, reason = ExposureManager.check_exposure(
            opportunity.symbol, 
            opportunity.exchange_spot, 
            opportunity.exchange_futures
        )
        if not ok:
            return False, reason, 0.0

        # 3. Dimensionamento (Position Sizing)
        score = getattr(opportunity, 'score', 50)
        size_usd = PositionSizer.calculate_size_usd(score)

        if size_usd <= 0:
            return False, "NO_CAPITAL_AVAILABLE", 0.0

        # 4. Alocação (Reserva de Capital)
        # Esta é a única operação que altera estado (Stateful)
        if not CapitalState.allocate(size_usd):
            return False, "ALLOCATION_FAILED", 0.0

        return True, "APPROVED", size_usd

    @staticmethod
    def process_exit(amount_usd: float, pnl_usd: float):
        """
        Processa a saída de um trade, devolvendo capital + PnL ao pool.
        """
        CapitalState.release(amount_usd, pnl_usd)