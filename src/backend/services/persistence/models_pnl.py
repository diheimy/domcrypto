from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from src.backend.services.persistence.database import Base

class PaperTradePnL(Base):
    __tablename__ = "paper_trade_pnl"

    id = Column(Integer, primary_key=True, index=True)
    
    # CORREÇÃO CRÍTICA: Tipo String para compatibilidade com UUID
    snapshot_id = Column(String, ForeignKey("paper_trades.id"), nullable=False, index=True)

    symbol = Column(String, index=True)
    direction = Column(String) # Opcional, mas bom para analytics rápido
    
    # Dados Financeiros Base
    capital_usd = Column(Float)
    entry_spot = Column(Float)   # Snapshot Spot
    entry_futures = Column(Float)# Snapshot Futures
    
    # Preços de Saída (Simulados)
    exit_spot = Column(Float)
    exit_futures = Column(Float)
    
    # Custos Operacionais
    fees_usd = Column(Float)
    funding_usd = Column(Float)
    
    # Resultado Final
    pnl_usd = Column(Float)      # Net PnL $
    pnl_pct = Column(Float)      # Net PnL %
    
    # Metadados de Tempo
    holding_seconds = Column(Integer)
    timestamp_open = Column(DateTime)
    timestamp_close = Column(DateTime)