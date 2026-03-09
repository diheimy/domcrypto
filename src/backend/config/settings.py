import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações Básicas
ENV = os.getenv("PYTHON_ENV", os.getenv("ENV", "development"))
DEBUG = os.getenv("DEBUG", "True") == "True"

# --- [MODO DO SISTEMA] ---
# 'LIVE': Kill Switch ativo, executa ordens reais se aprovado.
# 'PAPER': Executa ordens simuladas, Kill Switch ativo.
# 'SHADOW': Roda tudo, loga erros e Kill Switch (apenas aviso), mas NÃO TRAVA o pipeline.
# Ideal para calibração inicial.
SYSTEM_MODE = os.getenv("SYSTEM_MODE", "SHADOW")

# --- [MODO OBSERVAÇÃO] ---
# True: O sistema processa e exibe oportunidades com spread negativo ou
#       que não pagam a taxa, marcando-as como "OBSERVATION_ONLY".
# False: (Modo Produção) O sistema descarta silenciosamente qualquer
#        oportunidade que não gere lucro líquido imediato.
OBSERVATION_MODE = os.getenv("OBSERVATION_MODE", "True").lower() == "true"

# --- [FEE CONFIG] ---
# Taxa total estimada para entrar e sair da operação (Spot + Futuros).
# Padrão: 0.2% (0.1% Spot + 0.1% Futuros).
# No futuro (F8), isso será substituído pelo FeeService dinâmico.
ESTIMATED_TOTAL_FEE = float(os.getenv("ESTIMATED_TOTAL_FEE", "0.2"))

# --- [TRADING CONFIG] ---
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"
INITIAL_CAPITAL_USD = float(os.getenv("INITIAL_CAPITAL_USD", "10000"))
HEDGE_RATIO = float(os.getenv("HEDGE_RATIO", "1.0"))

# Filtros mínimos
MIN_SPREAD_PCT = float(os.getenv("MIN_SPREAD_PCT", "0.5"))
MIN_SCORE = int(os.getenv("MIN_SCORE", "50"))
MIN_VOLUME_24H_USD = float(os.getenv("MIN_VOLUME_24H_USD", "100000"))

# Risk management
DAILY_STOP_LOSS_PCT = float(os.getenv("DAILY_STOP_LOSS_PCT", "2.0"))
MAX_POSITION_PCT = float(os.getenv("MAX_POSITION_PCT", "10.0"))
MAX_DRAWDOWN_PCT = float(os.getenv("MAX_DRAWDOWN_PCT", "5.0"))

# --- [DATABASE] ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://domcrypto:password@localhost:5432/domcrypto"
)

# --- [EXCHANGES] ---
# Binance
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"

# Bybit
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")
BYBIT_TESTNET = os.getenv("BYBIT_TESTNET", "true").lower() == "true"

# MEXC
MEXC_API_KEY = os.getenv("MEXC_API_KEY", "")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET", "")

# --- [LOGGING] ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/domcrypto.log")
