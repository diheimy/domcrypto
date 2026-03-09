import logging
from sqlalchemy import func
from src.backend.services.persistence.database import SessionLocal
from src.backend.services.persistence.models import OpportunitySnapshot

logger = logging.getLogger("RiskMetrics")

class RiskMetrics:
    """
    Calcula métricas quantitativas de risco
    com base no histórico observado.
    """

    @staticmethod
    def diversification_index():
        """
        Mede o quão diversificado o sistema está (HHI - Herfindahl-Hirschman Index).
        0.0 = Diversificação total (infinitos ativos com peso igual)
        1.0 = Concentração total (tudo em um único ativo)
        """
        db = SessionLocal()
        try:
            total = db.query(func.count(OpportunitySnapshot.id)).scalar()
            if not total or total == 0:
                return 0.0

            symbols = (
                db.query(
                    OpportunitySnapshot.symbol,
                    func.count(OpportunitySnapshot.id).label("count")
                )
                .group_by(OpportunitySnapshot.symbol)
                .all()
            )

            # Soma dos quadrados das participações
            concentration = sum((row.count / total) ** 2 for row in symbols)
            return round(concentration, 4)

        finally:
            db.close()

    @staticmethod
    def high_score_dependency(threshold: float = 80.0):
        """
        Mede dependência de "balas de prata" (oportunidades perfeitas).
        Se o bot só acha oportunidade com score > 80, ele é frágil em mercados laterais.
        """
        db = SessionLocal()
        try:
            total = db.query(func.count(OpportunitySnapshot.id)).scalar()
            if not total or total == 0:
                return 0.0
            
            high_score_count = (
                db.query(func.count(OpportunitySnapshot.id))
                .filter(OpportunitySnapshot.score >= threshold)
                .scalar()
            )

            return round(high_score_count / total, 4)

        finally:
            db.close()