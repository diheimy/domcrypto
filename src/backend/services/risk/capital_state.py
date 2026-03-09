from dataclasses import dataclass
import logging

logger = logging.getLogger("RiskEngine")

@dataclass
class CapitalStateSnapshot:
    """Snapshot imutável do estado financeiro"""
    initial_capital: float
    current_capital: float
    allocated_capital: float
    free_capital: float
    peak_equity: float
    current_drawdown_pct: float

class CapitalState:
    """
    Fonte da Verdade Financeira (Ledger Contábil).
    
    NOTA ARQUITETURAL: 
    - _current_capital reflete apenas capital REALIZADO (trades fechados).
    - Não reflete flutuação de PnL aberto (Mark-to-Market).
    - Para Equity Curve em tempo real, consulte o serviço de Analytics.
    """
    
    _initial_capital: float = 1000.0
    _current_capital: float = 1000.0
    _allocated_capital: float = 0.0
    _peak_equity: float = 1000.0

    @classmethod
    def reset(cls, initial: float = 1000.0):
        cls._initial_capital = initial
        cls._current_capital = initial
        cls._allocated_capital = 0.0
        cls._peak_equity = initial

    @classmethod
    def allocate(cls, amount: float) -> bool:
        """Reserva capital para um novo trade."""
        if amount <= 0: return False
        
        if amount > cls.get_free_capital():
            return False
            
        cls._allocated_capital += amount
        return True

    @classmethod
    def release(cls, amount: float, pnl: float):
        """
        Libera capital alocado e contabiliza resultado.
        Input:
            amount: Valor original alocado (USD)
            pnl: Lucro/Prejuízo nominal (USD)
        """
        # Hardening: Validação de segurança
        if not isinstance(pnl, (int, float)):
            logger.error(f"CRITICAL: Tentativa de injetar PnL inválido no CapitalState: {pnl}")
            return # Ou raise ValueError, dependendo da política de erro

        # Libera alocação (garante não ficar negativo por erro de arredondamento)
        cls._allocated_capital = max(0.0, cls._allocated_capital - amount)
        
        # Atualiza saldo realizado
        cls._current_capital += pnl
        
        # Drawdown Calculation (Peak-to-Trough Realizado)
        if cls._current_capital > cls._peak_equity:
            cls._peak_equity = cls._current_capital

    @classmethod
    def get_free_capital(cls) -> float:
        return cls._current_capital - cls._allocated_capital

    @classmethod
    def get_drawdown_pct(cls) -> float:
        """Retorna drawdown realizado (ex: -5.0)"""
        if cls._peak_equity <= 0: return 0.0
        dd = (cls._current_capital - cls._peak_equity) / cls._peak_equity
        return dd * 100.0

    @classmethod
    def get_snapshot(cls) -> CapitalStateSnapshot:
        return CapitalStateSnapshot(
            initial_capital=cls._initial_capital,
            current_capital=cls._current_capital,
            allocated_capital=cls._allocated_capital,
            free_capital=cls.get_free_capital(),
            peak_equity=cls._peak_equity,
            current_drawdown_pct=cls.get_drawdown_pct()
        )