import logging
from src.backend.models.opportunity import Opportunity
from src.backend.services.persistence.models import OpportunitySnapshot
# Nova importação
from src.backend.utils.direction_helper import extract_direction

logger = logging.getLogger("SnapshotBuilder")

class SnapshotBuilder:
    """
    Responsável por converter uma Opportunity viva
    em um OpportunitySnapshot imutável para persistência.
    """

    @staticmethod
    def build(op: Opportunity, scoring_profile: str) -> OpportunitySnapshot:
        """
        Constrói um snapshot imutável a partir de uma Opportunity.
        """
        try:
            # 1. Extração de Direção (Delegada ao Helper)
            # Código limpo: o builder não conhece mais as strings mágicas
            direction = extract_direction(op.tags)

            snapshot = OpportunitySnapshot(
                symbol=op.symbol,
                exchange_spot=op.exchange_spot,
                exchange_futures=op.exchange_futures,

                spot_price=op.spot_price,
                futures_price=op.futures_price,
                spread_pct=op.spread_pct,
                volume_24h=op.volume_24h,

                direction=direction, # Valor vindo do helper
                score=op.score,
                scoring_profile=scoring_profile,

                health=op.health if op.health else {},
                tags=op.tags if op.tags else [],
            )

            return snapshot

        except Exception as e:
            logger.error(f"Erro ao construir snapshot para {op.symbol}: {e}")
            raise # Re-raise é correto aqui, pois falha de build é bug

    @staticmethod
    def build_batch(ops: list[Opportunity], scoring_profile: str) -> list[OpportunitySnapshot]:
        snapshots = []
        for op in ops:
            try:
                snapshots.append(SnapshotBuilder.build(op, scoring_profile))
            except Exception:
                continue
        return snapshots