import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.backend.services.persistence.models import OpportunitySnapshot
from src.backend.services.persistence.database import SessionLocal

logger = logging.getLogger("OpportunityQueries")

class OpportunityQueries:
    """
    Camada de leitura analítica do banco de histórico.
    Somente leitura.
    
    Responsável por recuperar dados brutos (Snapshots) para inspeção.
    """

    @staticmethod
    def get_latest(
        limit: int = 50,
        scoring_profile: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[OpportunitySnapshot]:
        """
        Busca os snapshots mais recentes, com filtros opcionais.
        Útil para: Tabela de 'Últimas Oportunidades' no Dashboard.
        """
        db: Session = SessionLocal()
        try:
            query = db.query(OpportunitySnapshot)

            # Filtro por perfil (ex: ver apenas o que o perfil 'aggressive' viu)
            if scoring_profile:
                query = query.filter(
                    OpportunitySnapshot.scoring_profile == scoring_profile
                )
            
            # Filtro por qualidade mínima
            if min_score > 0:
                query = query.filter(OpportunitySnapshot.score >= min_score)

            return (
                query
                .order_by(desc(OpportunitySnapshot.timestamp))
                .limit(limit)
                .all()
            )

        except Exception as e:
            logger.error(f"Erro ao buscar snapshots recentes: {e}")
            return []

        finally:
            db.close()
            
    @staticmethod
    def get_by_symbol(symbol: str, limit: int = 50) -> List[OpportunitySnapshot]:
        """
        Histórico específico de um ativo.
        Útil para: Clicar numa moeda e ver o comportamento passado dela.
        """
        db: Session = SessionLocal()
        try:
            return (
                db.query(OpportunitySnapshot)
                .filter(OpportunitySnapshot.symbol == symbol)
                .order_by(desc(OpportunitySnapshot.timestamp))
                .limit(limit)
                .all()
            )
        finally:
            db.close()