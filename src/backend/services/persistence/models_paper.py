from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean
from src.backend.services.persistence.database import Base
from datetime import datetime
import uuid

class PaperTradeSnapshot(Base):
    __tablename__ = "paper_trades"

    # ID como String (UUID)
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identidade
    symbol = Column(String, index=True)
    direction = Column(String)  # 'LONG-SHORT' ou 'SHORT-LONG'
    
    # Decisão
    execute = Column(Boolean)
    reason = Column(String)
    
    # Status do Trade (NOVO - ETAPA 8.4)
    # Permite filtrar rapidamente o que precisa de atenção
    is_open = Column(Boolean, default=True, index=True)
    
    # Financeiro Entrada
    capital_usd = Column(Float)
    spot_price = Column(Float)
    futures_price = Column(Float)
    spread_pct = Column(Float)
    spread_net_pct = Column(Float)
    
    # Inteligência
    score = Column(Float)
    scoring_profile = Column(String)
    health_score = Column(Float)
    
    # Metadados
    tags = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)