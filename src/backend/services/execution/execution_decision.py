from dataclasses import dataclass
from typing import Optional

from src.backend.models.opportunity import Opportunity
from src.backend.services.execution.execution_context import ExecutionContext
from src.backend.services.execution.risk_gate import RiskGate
from src.backend.services.execution.position_sizer import PositionSizer

@dataclass(frozen=True)
class ExecutionDecision:
    """
    Representa a decisão final do sistema sobre uma oportunidade.
    É o contrato entre a Camada de Inteligência e a Camada de Ação.
    """
    execute: bool
    reason: str
    capital_usd: float = 0.0
    symbol: str = ""  # Redundância útil para logs

class ExecutionDecisionEngine:
    """
    Orquestrador da decisão de execução.
    Combina Contexto, Regras e Sizing.
    """

    @staticmethod
    def decide(
        op: Opportunity,
        ctx: ExecutionContext,
        base_capital_usd: float
    ) -> ExecutionDecision:
        
        # 1. Verifica Portões de Risco
        if not RiskGate.allow(op, ctx):
            return ExecutionDecision(
                execute=False,
                reason="Blocked by RiskGate (Score/Health/Context)",
                symbol=op.symbol
            )

        # 2. Calcula Tamanho da Posição
        capital = PositionSizer.size(op, base_capital_usd)
        
        # Proteção final de sizing
        if capital <= 0:
             return ExecutionDecision(
                execute=False,
                reason="Zero Capital Allocated",
                symbol=op.symbol
            )

        # 3. Aprova Execução
        return ExecutionDecision(
            execute=True,
            reason="Approved",
            capital_usd=round(capital, 2),
            symbol=op.symbol
        )