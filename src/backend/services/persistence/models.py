import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON
from src.backend.services.persistence.database import Base

class OpportunitySnapshot(Base):
    """
    Tabela 'opportunity_snapshots'.
    Representa uma foto imutável de uma oportunidade processada pelo pipeline.
    
    Este modelo é otimizado para escrita (Append-Only) e análise posterior.
    """
    __tablename__ = "opportunity_snapshots"

    # Identidade e Tempo
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Contexto do Ativo
    symbol = Column(String, index=True)       # Ex: BTCUSDT
    exchange_spot = Column(String)            # Ex: Binance
    exchange_futures = Column(String)         # Ex: Mexc

    # Dados de Mercado (Fatos Numéricos)
    spot_price = Column(Float)
    futures_price = Column(Float)
    spread_pct = Column(Float)
    volume_24h = Column(Float)

    # Inteligência V2 (Resultados do Pipeline)
    direction = Column(String)                # Ex: spot_to_futures
    score = Column(Float)                     # Ex: 85.4
    scoring_profile = Column(String)          # Ex: balanced

    # Contexto Rico (Para Auditoria e Backtest Avançado)
    health = Column(JSON)                     # Estado completo do Market Health
    tags = Column(JSON)                       # Tags aplicadas (ex: ["high_liquidity"])