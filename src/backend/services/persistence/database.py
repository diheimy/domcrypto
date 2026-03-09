import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger("PersistenceDB")

# Banco dedicado ao histórico (V2)
# Isolado do banco de execução (V1) para evitar locks e concorrência
SQLALCHEMY_DATABASE_URL = "sqlite:///./history.db"

# check_same_thread=False é obrigatório para SQLite em ambiente async (FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Fabrica de sessões para operações de escrita/leitura
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para os Models
Base = declarative_base()

def init_history_db():
    """
    Cria as tabelas do histórico se não existirem.
    Deve ser chamado no startup do app.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Persistence Service: Banco de Histórico (history.db) pronto.")
    except Exception as e:
        logger.error(f"❌ Persistence Service Erro: Falha ao iniciar DB: {e}")

def get_db():
    """Generator para injeção de dependência (se necessário futuramente)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()