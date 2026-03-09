import logging
from src.backend.models.opportunity import Opportunity
from src.backend.services.execution.execution_context import ExecutionContext

logger = logging.getLogger("RiskGate")

class RiskGate:
    """
    Porta lógica de autorização (Firewall de Execução).
    Decide SIM ou NÃO para uma oportunidade específica.
    """

    @staticmethod
    def allow(op: Opportunity, ctx: ExecutionContext) -> bool:
        # 1️⃣ Kill Switch Sistêmico
        if not ctx.is_healthy:
            # logger.warning("RiskGate: Bloqueio sistêmico (Contexto não saudável).")
            return False

        # 2️⃣ Qualidade Mínima Operacional (Filtro de Execução, não de Visualização)
        # Oportunidades com score 40 podem ser visualizadas, mas não operadas.
        if op.score < 60:
            return False

        # 3️⃣ Proteção de Anomalia de Spread (Fat finger protection)
        # Spread negativo (exceto se for reverse, mas por segurança bloqueamos na V1)
        # Spread > 50% em crypto major é quase sempre erro de API ou moeda morta.
        if op.spread_pct <= 0 or op.spread_pct > 50:
            logger.warning(f"RiskGate: Spread anômalo detectado em {op.symbol} ({op.spread_pct}%)")
            return False

        # 4️⃣ Validação de Liquidez (Redundância de segurança)
        # Se por algum motivo o HealthEngine falhou ou não rodou
        if not op.health or not op.health.get("healthy", False):
            return False

        return True