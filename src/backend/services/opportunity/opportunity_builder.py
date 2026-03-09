import logging
from typing import List
from src.backend.models.opportunity import Opportunity

logger = logging.getLogger("OpportunityBuilder")

class OpportunityBuilder:
    """
    Responsável por consolidar e finalizar o objeto Opportunity
    após todos os sensores e engines terem rodado.
    Garante que o objeto esteja coerente, limpo e pronto para consumo.
    """

    @staticmethod
    def build(op: Opportunity) -> Opportunity:
        """
        Garante consistência final do objeto Opportunity.
        Não filtra, não pontua, não decide.
        """

        # 1️⃣ Garantia defensiva: tags únicas
        # Remove duplicatas que podem ter sido adicionadas por múltiplos engines
        if op.tags:
            op.tags = list(set(op.tags))

        # 2️⃣ Normalização final de valores numéricos
        # Proteção contra dízimas periódicas ou precisão excessiva de float
        if op.spread_pct is not None:
            op.spread_pct = round(op.spread_pct, 4)
        
        if op.volume_24h is not None:
            op.volume_24h = round(op.volume_24h, 2)

        # Arredonda spread líquido se existir (Etapa 3.2)
        if getattr(op, 'spread_net_pct', None) is not None:
            op.spread_net_pct = round(op.spread_net_pct, 4)

        # 3️⃣ Placeholder explícito para score (etapa futura)
        # Garante que nunca seja None para evitar erros matemáticos
        if op.score is None:
            op.score = 0.0

        # 4️⃣ Placeholder explícito para health (etapa 2)
        # Garante que UI sempre receba um dict, mesmo vazio
        if op.health is None:
            op.health = {}

        return op

    @staticmethod
    def build_batch(ops: List[Opportunity]) -> List[Opportunity]:
        """
        Aplica o builder em lote para todas as oportunidades.
        """
        return [OpportunityBuilder.build(op) for op in ops]