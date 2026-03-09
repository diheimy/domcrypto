# Backend Python - Especificação de Desenvolvimento

**DomCrypto Bot** - Sistema de Arbitragem de Criptomoedas
Versão: 0.2.0 | Data: 2026-03-08

---

## 📋 Visão Geral

Backend FastAPI para processamento de oportunidades de arbitragem entre mercados Spot e Futuros.

### Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  OPPORTUNITY PIPELINE (ciclo 3s)                     │   │
│  │  Fetch → Normalize → Build → Score → Persist → WS   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │  Fetch   │ Funding  │ Quality  │ Execution│  Risk    │  │
│  │  Service │ Engine   │ Engine   │ Engine   │  Engine  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              PostgreSQL + SQLAlchemy                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         WebSocket / SSE (Real-time Updates)          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Pastas

```
src/backend/
├── __init__.py
├── main.py                      # App FastAPI, lifespan, WebSocket manager
├── api/
│   ├── __init__.py
│   ├── routes.py                # Router aggregation
│   ├── schemas.py               # Pydantic schemas
│   ├── adapters/
│   │   └── opportunity_ui_adapter.py   # Adapter para frontend
│   └── endpoints/
│       └── websocket.py                # WebSocket endpoint
├── config/
│   ├── __init__.py
│   ├── config.py              # Configurações gerais
│   ├── constants.py           # Constantes do domínio
│   ├── modes.py               # Modos de operação
│   └── settings.py            # Settings (env vars)
├── domain/
│   ├── __init__.py
│   └── opportunity_dto.py     # Domain DTOs
├── models/
│   ├── __init__.py
│   ├── opportunity.py         # Model Opportunity
│   ├── paper_trade.py         # Model PaperTrade
│   ├── spread_engine.py       # Cálculo de spread
│   └── trade_history.py       # Histórico de trades
├── pipeline/
│   ├── __init__.py
│   ├── hard_rules.py          # Regras de filtro
│   ├── normalizer.py          # Normalização de dados
│   ├── opportunity_builder.py # Builder de oportunidades
│   └── opportunity_pipeline.py# Pipeline principal
├── schemas/
│   ├── __init__.py
│   └── v1_contract.py         # Contrato de dados V1
├── services/
│   ├── analytics/             # Analytics e métricas
│   ├── arbitrage/             # Lógica de arbitragem
│   ├── backtest/              # Backtest engine
│   ├── capital/               # Gestão de capital
│   ├── execution/             # Execução de ordens
│   ├── exit/                  # Estratégia de saída
│   ├── fees/                  # Cálculo de taxas
│   ├── fetch/                 # Fetch de dados exchanges
│   ├── funding/               # Funding rate
│   ├── history/               # Histórico de trades
│   ├── kill_switch/           # Kill switch global
│   ├── market_data/           # Dados de mercado
│   ├── market_health/         # Saúde do mercado
│   ├── market_regime/         # Regime de mercado
│   ├── opportunity/           # Gestão de oportunidades
│   ├── paper/                 # Paper trading
│   ├── persistence/           # Persistência DB
│   ├── quality/               # Quality scoring
│   ├── rebalance/             # Rebalanceamento
│   ├── risk/                  # Risk management
│   ├── scoring/               # Scoring engine
│   ├── simulation/            # Simulações
│   ├── storage/               # Storage de snapshots
│   └── trust/                 # Trust scoring
├── static/                    # Assets estáticos
├── templates/                 # Templates Jinja2
└── utils/
    ├── __init__.py
    ├── direction_helper.py    # Helpers de direção
    └── logging.py             # Config de logs
```

---

## 🔌 API Endpoints

### HTTP Endpoints

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/api/v1/opportunities` | Lista oportunidades | ❌ |
| `GET` | `/api/v1/opportunities/{id}` | Detalhes da oportunidade | ❌ |
| `GET` | `/api/v1/settings` | Configurações do usuário | ❌ |
| `PUT` | `/api/v1/settings` | Atualiza configurações | ❌ |
| `GET` | `/api/v1/pnl` | Registro de PnL | ❌ |
| `GET` | `/api/v1/snapshots` | Pipeline snapshots | ❌ |

### WebSocket Endpoints

| Endpoint | Descrição | Payload |
|----------|-----------|---------|
| `WS /ws/opportunities` | Updates em tempo real | `OpportunityItemV2[]` |

---

## 📊 Models de Dados

### Opportunity (JSONB Payload)

```python
class OpportunityItemV2:
    # Identidade
    id: str                    # "BTC-binance-binance_futures"
    symbol: str                # "BTC"
    pair: str                  # "BTC/USDT"
    exchange_spot: str         # "binance"
    exchange_futures: str      # "binance_futures"
    is_cross_venue: bool       # True se exchanges diferentes

    # Preços
    price_spot: float
    price_futures: float

    # Spread
    spread_exec_pct: float     # Spread bruto
    spread_net_pct: float      # Spread após fees

    # ROI e Capacidade
    roi_net_pct: float
    profit_usd: float
    capacity_pct: float
    capacity_band: Literal["GREEN", "YELLOW", "RED"]
    entry_leg_usd: float

    # Liquidez
    spot_top_book_usd: float
    futures_top_book_usd: float
    volume_24h_usd: int

    # Funding
    funding_rate: float
    funding_interval_hours: int
    next_funding_at: int | None

    # Execução
    orders_to_fill_spot: int
    orders_to_fill_fut: int
    fill_status: str

    # Score e Status
    score: int                 # 0-100
    trust_score: int           # 0-100
    quality_level: str
    status: Literal["ACTIVE", "READY", "OBSERVATION_ONLY", "KILLED"]
    execution_decision: str

    # Meta
    persistence_minutes: int
    tags: list[str]
    ts_created: int
    ts_updated: int
```

### UserSettings

```python
class UserSettings:
    profile_name: str = "default"
    min_spread_pct: float = 0.5
    min_score: int = 50
    min_volume_usd: int = 100000
    min_persistence_min: int = 0
    bankroll_usd: float = 10000
    hedge_pct: float = 100
    entry_min_usd: float = 100
    entry_max_usd: float = 1000
    hide_blocked: bool = False
    allow_cross: bool = True
    allow_same: bool = True
    spots: list[str] = ["binance", "mexc", "bybit"]
    futures: list[str] = ["binance_futures", "mexc_futures"]
    blocked_coins: list[str] = []
```

---

## 🔧 Serviços Principais

### 1. OpportunityPipeline

**Responsabilidade:** Orquestrar o ciclo de processamento de oportunidades.

```python
class OpportunityPipeline:
    async def run_cycle(self) -> List[Opportunity]:
        # 1. Fetch dados das exchanges
        # 2. Normalizar dados
        # 3. Builder de oportunidades
        # 4. Hard rules (filtros)
        # 5. Scoring
        # 6. Persistir no DB
        # 7. Broadcast via WebSocket
        pass
```

**Ciclo:** 3 segundos

### 2. FetchService

**Responsabilidade:** Buscar dados das exchanges (ccxt).

```python
class FetchService:
    async def fetch_tickers(self, exchanges: List[str]) -> Dict:
        pass

    async def fetch_orderbook(self, exchange: str, symbol: str) -> Dict:
        pass

    async def fetch_funding_rate(self, exchange: str, symbol: str) -> float:
        pass
```

### 3. QualityEngine

**Responsabilidade:** Calcular score de qualidade da oportunidade.

```python
class QualityEngine:
    def calculate_score(self, opp: Opportunity) -> int:
        # Fatores:
        # - Spread líquido
        # - Volume 24h
        # - Liquidez do book
        # - Funding rate
        # - Persistência
        # - Trust score
        pass
```

### 4. RiskEngine

**Responsabilidade:** Gerenciar risco e posição.

```python
class RiskEngine:
    def check_drawdown_limit(self) -> bool:
        pass

    def calculate_position_size(self, opp: Opportunity) -> float:
        pass

    def check_daily_loss_limit(self) -> bool:
        pass
```

### 5. ExecutionEngine

**Responsabilidade:** Executar ordens nas exchanges.

```python
class ExecutionEngine:
    async def execute_spot_buy(self, opp: Opportunity, size: float):
        pass

    async def execute_futures_short(self, opp: Opportunity, size: float):
        pass

    async def close_position(self, opp: Opportunity):
        pass
```

---

## 🗄️ Database Schema

```sql
-- Oportunidades atuais
CREATE TABLE opportunities (
  symbol            VARCHAR(20)   NOT NULL,
  exchange_spot     VARCHAR(30)   NOT NULL,
  exchange_futures  VARCHAR(30)   NOT NULL,
  payload           JSONB         NOT NULL,
  score             SMALLINT      NOT NULL DEFAULT 0,
  spread_net_pct    DECIMAL(8,4)  NOT NULL DEFAULT 0,
  volume_24h_usd    BIGINT        NOT NULL DEFAULT 0,
  status            VARCHAR(20)   NOT NULL DEFAULT 'OBSERVATION_ONLY',
  capacity_band     VARCHAR(10)   NOT NULL DEFAULT 'RED',
  first_seen_at     TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  PRIMARY KEY (symbol, exchange_spot, exchange_futures)
);

-- Pipeline snapshots
CREATE TABLE pipeline_snapshots (
  id            BIGSERIAL     PRIMARY KEY,
  cycle_id      INTEGER       NOT NULL,
  ts            TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  count_raw     SMALLINT      NOT NULL DEFAULT 0,
  count_active  SMALLINT      NOT NULL DEFAULT 0,
  count_obs     SMALLINT      NOT NULL DEFAULT 0,
  count_killed  SMALLINT      NOT NULL DEFAULT 0,
  top_spread    DECIMAL(8,4),
  top_symbol    VARCHAR(20),
  meta          JSONB
);

-- Configurações
CREATE TABLE user_settings (
  id            SERIAL        PRIMARY KEY,
  profile_name  VARCHAR(50)   NOT NULL DEFAULT 'default',
  settings      JSONB         NOT NULL,
  updated_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  UNIQUE(profile_name)
);

-- PnL records
CREATE TABLE pnl_records (
  id               BIGSERIAL     PRIMARY KEY,
  symbol           VARCHAR(20)   NOT NULL,
  exchange_spot    VARCHAR(30)   NOT NULL,
  exchange_futures VARCHAR(30)   NOT NULL,
  entry_at         TIMESTAMPTZ   NOT NULL,
  exit_at          TIMESTAMPTZ,
  entry_spread     DECIMAL(8,4),
  exit_spread      DECIMAL(8,4),
  capital_usd      DECIMAL(12,2),
  pnl_usd          DECIMAL(12,2),
  pnl_pct          DECIMAL(8,4),
  fees_usd         DECIMAL(12,2),
  status           VARCHAR(20)   NOT NULL DEFAULT 'OPEN',
  meta             JSONB
);
```

---

## 🔐 Configurações (.env)

```bash
# App
PYTHON_ENV=development
DEBUG=True

# Sistema
SYSTEM_MODE=SHADOW        # LIVE, PAPER, SHADOW
OBSERVATION_MODE=True

# Database
DATABASE_URL=postgresql://domcrypto:password@localhost:5432/domcrypto

# Exchanges
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_TESTNET=true

BYBIT_API_KEY=
BYBIT_API_SECRET=
BYBIT_TESTNET=true

# Trading
PAPER_TRADING=true
INITIAL_CAPITAL_USD=10000
HEDGE_RATIO=1.0

# Filtros
MIN_SPREAD_PCT=0.5
MIN_SCORE=50
MIN_VOLUME_24H_USD=100000

# Risk
DAILY_STOP_LOSS_PCT=2.0
MAX_POSITION_PCT=10.0
MAX_DRAWDOWN_PCT=5.0

# Logs
LOG_LEVEL=INFO
LOG_FILE=logs/domcrypto.log
```

---

## 📝 Padrões de Código

### Style Guide
- **Type hints:** Obrigatórios
- **Docstrings:** Google style
- **Format:** Black, Flake8, MyPy
- **Imports:** Ordem alfabética, standard lib primeiro

### Estrutura de Arquivo
```python
"""Docstring do módulo."""

# 1. Standard library
import asyncio
import logging

# 2. Third party
from fastapi import FastAPI
import ccxt

# 3. Local imports
from src.backend.services.fetch import FetchService

# Constants
CONSTANT = "value"

# Classes e funções
class MyClass:
    """Docstring da classe."""
    pass

def my_function(arg: str) -> str:
    """Docstring da função."""
    pass
```

---

## 🧪 Testes

```bash
# Rodar testes
pytest

# Com coverage
pytest --cov=src/backend

# Testes específicos
pytest tests/test_opportunity_pipeline.py
```

### Estrutura de Testes
```
tests/
├── unit/
│   ├── test_spread_engine.py
│   ├── test_quality_engine.py
│   └── test_risk_engine.py
├── integration/
│   ├── test_fetch_service.py
│   └── test_pipeline.py
└── e2e/
    └── test_full_cycle.py
```

---

## 🚀 Comandos

```bash
# Desenvolvimento
python src/backend/main.py
python run_backend.py

# Testes
pytest
pytest --cov=src/backend

# Code quality
black src/backend/
flake8 src/backend/
mypy src/backend/

# Docker
docker-compose up -d python-backend
docker-compose logs -f python-backend
```

---

## 📈 Métricas e Monitoramento

### Pipeline Metrics
- `cycle_duration_ms`: Tempo do ciclo
- `opportunities_count`: Oportunidades processadas
- `active_count`: Oportunidades ativas
- `broadcast_latency_ms`: Latência do broadcast

### Risk Metrics
- `daily_pnl_usd`: PnL diário
- `drawdown_pct`: Drawdown atual
- `exposure_pct`: Exposição atual

### System Metrics
- `websocket_connections`: Conexões WS ativas
- `db_query_time_ms`: Tempo de query DB
- `error_rate`: Taxa de erros
