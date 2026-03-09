from dataclasses import dataclass

@dataclass
class RiskProfileConfig:
    name: str
    max_risk_per_trade_pct: float  # Decimal: 0.10 = 10%
    max_open_trades: int           # Inteiro
    max_drawdown_limit_pct: float  # Decimal: -0.10 = -10%
    stop_loss_limit_pct: float     # Decimal: -0.02 = -2%

class RiskProfile:
    """
    Define os perfis de risco.
    PADRÃO DE UNIDADE: DECIMAIS MATEMÁTICOS.
    Ex: 10% = 0.10, -5% = -0.05
    """
    
    CONSERVATIVE = RiskProfileConfig(
        name="CONSERVATIVE",
        max_risk_per_trade_pct=0.10, # 10%
        max_open_trades=3,
        max_drawdown_limit_pct=-0.05, # -5%
        stop_loss_limit_pct=-0.02     # -2%
    )

    MODERATE = RiskProfileConfig(
        name="MODERATE",
        max_risk_per_trade_pct=0.20, # 20%
        max_open_trades=5,
        max_drawdown_limit_pct=-0.10, # -10%
        stop_loss_limit_pct=-0.05     # -5%
    )

    AGGRESSIVE = RiskProfileConfig(
        name="AGGRESSIVE",
        max_risk_per_trade_pct=0.50, # 50%
        max_open_trades=10,
        max_drawdown_limit_pct=-0.20, # -20%
        stop_loss_limit_pct=-0.10     # -10%
    )

    _current: RiskProfileConfig = MODERATE

    @classmethod
    def set_profile(cls, profile_name: str):
        if profile_name == "CONSERVATIVE": cls._current = cls.CONSERVATIVE
        elif profile_name == "AGGRESSIVE": cls._current = cls.AGGRESSIVE
        else: cls._current = cls.MODERATE

    @classmethod
    def get(cls) -> RiskProfileConfig:
        return cls._current