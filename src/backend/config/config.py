# Configurações Globais do Sistema

# Filtros de Qualidade (Hard Rules)
BACKEND_MIN_VOLUME_USD = 50_000.0  # Volume mínimo 50k
BACKEND_MIN_SPREAD_PCT = 0.20      # Spread mínimo 0.20%

# Lista de bloqueio (Moedas instáveis ou fiat)
BLACKLIST_COINS = {
    'USDC', 'BUSD', 'DAI', 'TUSD', 'EUR', 'GBP', 
    'UP', 'DOWN', 'BULL', 'BEAR', 'QUIC', 'GALA'
}