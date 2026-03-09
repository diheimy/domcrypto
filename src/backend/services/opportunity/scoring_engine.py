import math
import logging
from src.backend.models.opportunity import Opportunity
from src.backend.services.opportunity.scoring_profiles import ScoringProfile
from src.backend.services.opportunity.scoring_weights import SCORING_WEIGHTS

logger = logging.getLogger("ScoringEngine")

class ScoringEngine:
    """
    Classificador de oportunidades com suporte a múltiplos perfis de risco.
    Stateless: O perfil é passado no momento do cálculo.
    """

    # -------------------------
    # Bias Direcional (V1) - Mantido constante por enquanto
    # -------------------------
    DIRECTION_BIAS = {
        "spot_to_futures": 1.0,
        "futures_to_spot": 0.85,
    }

    @staticmethod
    def score(
        op: Opportunity, 
        profile: ScoringProfile = ScoringProfile.BALANCED
    ) -> Opportunity:
        """
        Calcula o score final baseado no perfil escolhido.
        """
        try:
            # Busca os pesos corretos para o perfil (O(1) lookup)
            weights = SCORING_WEIGHTS[profile.value]

            spread_score = ScoringEngine._spread_score(op)
            liquidity_score = ScoringEngine._liquidity_score(op)
            health_score = ScoringEngine._health_score(op)
            direction_score = ScoringEngine._direction_score(op)

            # Combinação Ponderada Dinâmica
            raw_score = (
                spread_score * weights.spread +
                liquidity_score * weights.liquidity +
                health_score * weights.health +
                direction_score * weights.direction
            )
            
            # Ajuste de Escala (Mantido fator 20.0 para legibilidade 0-100)
            final_score = raw_score * 20.0 

            op.score = round(max(final_score, 0.0), 2)

        except Exception as e:
            logger.error(f"Erro ao calcular score ({op.symbol}): {e}")
            op.score = 0.0

        return op

    # ------------------------------------------------------------------
    # Subscores (Mantidos idênticos à Etapa 4.1 - Reuso total)
    # ------------------------------------------------------------------
    @staticmethod
    def _spread_score(op: Opportunity) -> float:
        val = op.spread_pct or 0.0
        if val <= 0: return 0.0
        return math.log1p(val)

    @staticmethod
    def _liquidity_score(op: Opportunity) -> float:
        liquidity_usd = 0.0
        volume_24h = op.volume_24h or 0.0
        if op.health and isinstance(op.health, dict):
            liquidity_usd = op.health.get("total_liquidity_usd", 0.0)
        
        score_liq = math.log10(liquidity_usd + 1) if liquidity_usd > 0 else 0
        score_vol = math.log10(volume_24h + 1) if volume_24h > 0 else 0
        return (score_liq * 0.7) + (score_vol * 0.3)

    @staticmethod
    def _health_score(op: Opportunity) -> float:
        if not op.health or not isinstance(op.health, dict):
            return 0.0
        if not op.health.get("healthy", False):
            return 0.5
        imbalance = op.health.get("imbalance", 0.0)
        return max(0.0, 1.0 - imbalance)

    @staticmethod
    def _direction_score(op: Opportunity) -> float:
        if not op.tags: return 1.0
        for tag, bias in ScoringEngine.DIRECTION_BIAS.items():
            if tag in op.tags: return bias
        return 1.0

    # ------------------------------------------------------------------
    # Lote Dinâmico
    # ------------------------------------------------------------------
    @staticmethod
    def score_batch(
        ops: list[Opportunity], 
        profile: ScoringProfile = ScoringProfile.BALANCED
    ) -> list[Opportunity]:
        """
        Aplica scoring em lote usando o perfil especificado.
        """
        return [ScoringEngine.score(op, profile) for op in ops]