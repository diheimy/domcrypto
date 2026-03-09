import logging
from sqlalchemy import func, desc
from src.backend.services.persistence.database import SessionLocal
from src.backend.services.persistence.models import OpportunitySnapshot

logger = logging.getLogger("OpportunityAggregations")

class OpportunityAggregations:
    """
    Motor de inteligência analítica.
    Transforma dados históricos em métricas consolidadas (KPIs).
    """

    @staticmethod
    def top_symbols_by_avg_score(limit: int = 10):
        """
        Retorna os pares com melhor qualidade média histórica.
        Pergunta respondida: "Quais moedas costumam dar as melhores oportunidades?"
        """
        db = SessionLocal()
        try:
            return (
                db.query(
                    OpportunitySnapshot.symbol,
                    func.avg(OpportunitySnapshot.score).label("avg_score"),
                    func.count(OpportunitySnapshot.id).label("occurrences")
                )
                .group_by(OpportunitySnapshot.symbol)
                .having(func.count(OpportunitySnapshot.id) > 5) # Remove ruído (mínimo 5 aparições)
                .order_by(desc("avg_score"))
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"Erro na agregação top_symbols: {e}")
            return []
        finally:
            db.close()

    @staticmethod
    def avg_score_by_profile():
        """
        Compara a performance relativa dos perfis de risco.
        Pergunta respondida: "O perfil Agressivo realmente acha coisas melhores?"
        """
        db = SessionLocal()
        try:
            return (
                db.query(
                    OpportunitySnapshot.scoring_profile,
                    func.avg(OpportunitySnapshot.score).label("avg_score"),
                    func.count(OpportunitySnapshot.id).label("total_opportunities")
                )
                .group_by(OpportunitySnapshot.scoring_profile)
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def direction_distribution():
        """
        Analisa o viés do mercado.
        Pergunta respondida: "O mercado está mais para Contango (Spot < Fut) ou Backwardation?"
        """
        db = SessionLocal()
        try:
            return (
                db.query(
                    OpportunitySnapshot.direction,
                    func.count(OpportunitySnapshot.id).label("count"),
                    func.avg(OpportunitySnapshot.score).label("avg_score")
                )
                .group_by(OpportunitySnapshot.direction)
                .all()
            )
        finally:
            db.close()