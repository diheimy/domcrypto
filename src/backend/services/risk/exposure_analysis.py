import logging
from sqlalchemy import func, desc
from src.backend.services.persistence.database import SessionLocal
from src.backend.services.persistence.models import OpportunitySnapshot

logger = logging.getLogger("ExposureAnalysis")

class ExposureAnalysis:
    """
    Analisa concentração de oportunidades.
    NÃO executa trades.
    NÃO altera estado.
    Apenas leitura estratégica para identificar vícios do sistema.
    """

    @staticmethod
    def symbol_concentration(limit: int = 10):
        """
        Retorna os símbolos mais frequentes no histórico.
        Mede risco de overexposure por ativo.
        """
        db = SessionLocal()
        try:
            return (
                db.query(
                    OpportunitySnapshot.symbol,
                    func.count(OpportunitySnapshot.id).label("occurrences"),
                    func.avg(OpportunitySnapshot.score).label("avg_score")
                )
                .group_by(OpportunitySnapshot.symbol)
                .order_by(desc("occurrences"))
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def exchange_concentration():
        """
        Mede dependência excessiva de exchanges específicas.
        Se 100% das oportunidades são Binance->Mexc, uma falha na Mexc para o bot.
        """
        db = SessionLocal()
        try:
            return (
                db.query(
                    OpportunitySnapshot.exchange_spot,
                    OpportunitySnapshot.exchange_futures,
                    func.count(OpportunitySnapshot.id).label("occurrences")
                )
                .group_by(
                    OpportunitySnapshot.exchange_spot,
                    OpportunitySnapshot.exchange_futures
                )
                .order_by(desc("occurrences"))
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def direction_concentration():
        """
        Mede viés operacional (spot->futures vs futures->spot).
        Essencial para saber se o bot está apenas operando Bull Market (Contango).
        """
        db = SessionLocal()
        try:
            return (
                db.query(
                    OpportunitySnapshot.direction,
                    func.count(OpportunitySnapshot.id).label("occurrences"),
                    func.avg(OpportunitySnapshot.score).label("avg_score")
                )
                .group_by(OpportunitySnapshot.direction)
                .all()
            )
        finally:
            db.close()