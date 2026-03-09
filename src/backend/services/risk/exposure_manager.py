from src.backend.services.paper.paper_ledger import PaperLedger
from src.backend.services.risk.risk_profile import RiskProfile

class ExposureManager:
    """
    Controla a exposição sistêmica (concentração de risco).
    """

    @staticmethod
    def check_exposure(symbol: str, spot_ex: str, fut_ex: str) -> tuple[bool, str]:
        profile = RiskProfile.get()
        stats = PaperLedger.get_stats()
        active_count = stats.get("active_count", 0)

        # 1. Limite Global de Trades Simultâneos
        if active_count >= profile.max_open_trades:
            return False, f"MAX_TRADES ({active_count}/{profile.max_open_trades})"

        # 2. V2 Roadmap: Limite por Exchange (Risco de Custódia)
        # 3. V2 Roadmap: Correlação de Ativos
        
        return True, "OK"