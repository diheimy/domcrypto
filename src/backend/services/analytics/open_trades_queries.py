from sqlalchemy.orm import Session
from src.backend.services.persistence.database import SessionLocal
from src.backend.services.persistence.models_paper import PaperTradeSnapshot

class OpenTradesQueries:
    """
    Camada de leitura otimizada para trades abertos.
    Isola o ORM da lógica de negócio.
    """
    
    @staticmethod
    def get_open_trades(limit: int = 100):
        db: Session = SessionLocal()
        try:
            return (
                db.query(PaperTradeSnapshot)
                .filter(PaperTradeSnapshot.is_open == True)
                .order_by(PaperTradeSnapshot.timestamp.asc()) # FIFO: Trata os mais antigos primeiro
                .limit(limit)
                .all()
            )
        finally:
            db.close()