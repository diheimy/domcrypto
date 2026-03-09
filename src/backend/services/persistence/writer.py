import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from src.backend.services.persistence.database import SessionLocal
from src.backend.services.persistence.models import OpportunitySnapshot

logger = logging.getLogger("PersistenceWriter")

class PersistenceWriter:
    """
    Responsável por persistir snapshots no banco de histórico (history.db).

    - Fail-safe: nunca propaga exceções para o pipeline
    - Suporta escrita em lote
    - Controle explícito de sessão, commit e rollback
    """

    @staticmethod
    def write(snapshot: OpportunitySnapshot) -> bool:
        """
        Persiste um único snapshot.
        Retorna True se sucesso, False se falha.
        Útil para testes ou gravações pontuais.
        """
        db = SessionLocal()
        try:
            db.add(snapshot)
            db.commit()
            return True

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Erro ao persistir snapshot ({snapshot.symbol}): {e}")
            return False

        finally:
            db.close()

    @staticmethod
    def write_batch(snapshots: List[OpportunitySnapshot]) -> int:
        """
        Persiste múltiplos snapshots em uma única transação (Atômico).
        Se um falhar, todos falham (Rollback total), mantendo consistência.

        Retorna:
        - Quantidade de registros gravados com sucesso
        """
        if not snapshots:
            return 0

        db = SessionLocal()
        try:
            db.add_all(snapshots)
            db.commit()
            # logger.info(f"Persistência: {len(snapshots)} snapshots salvos.")
            return len(snapshots)

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Erro ao persistir batch de snapshots ({len(snapshots)}): {e}")
            return 0

        finally:
            db.close()