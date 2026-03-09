# Backend Python - DomCrypto

Backend FastAPI para processamento de oportunidades de arbitragem entre mercados Spot e Futuros.

## 📋 Visão Geral

- **Framework:** FastAPI 0.109+
- **Python:** 3.11+
- **Database:** PostgreSQL + SQLAlchemy
- **Exchanges:** CCXT (async)
- **Real-time:** WebSocket

## 🏗️ Arquitetura

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

## 📁 Estrutura de Pastas

```
src/backend/
├── __init__.py
├── main.py                      # App FastAPI, lifespan, WebSocket manager
├── database.py                  # Conexão PostgreSQL, session management
├── api/
│   ├── __init__.py
│   ├── routes.py                # Router aggregation
│   ├── schemas.py               # Pydantic schemas
│   ├── adapters/
│   │   └── opportunity_ui_adapter.py
│   └── endpoints/
│       ├── http_endpoints.py    # HTTP endpoints (/api/v1/*)
│       └── websocket.py         # WebSocket endpoint
├── config/
│   ├── __init__.py
│   ├── config.py                # Configurações gerais
│   ├── constants.py             # Constantes do domínio
│   ├── modes.py                 # Modos de operação
│   └── settings.py              # Settings (env vars)
├── domain/
│   ├── __init__.py
│   └── opportunity_dto.py       # Domain DTOs (OpportunityItemV2)
├── models/
│   ├── __init__.py              # SQLAlchemy models
│   ├── opportunity.py           # Model Opportunity
│   ├── paper_trade.py           # Model PaperTrade
│   ├── spread_engine.py         # Cálculo de spread
│   └── trade_history.py         # Histórico de trades
├── pipeline/
│   ├── __init__.py
│   ├── hard_rules.py            # Regras de filtro
│   ├── normalizer.py            # Normalização de dados
│   ├── opportunity_builder.py   # Builder de oportunidades
│   └── opportunity_pipeline.py  # Pipeline principal
├── schemas/
│   ├── __init__.py
│   └── v1_contract.py           # Contrato de dados V1
├── services/
│   ├── analytics/               # Analytics e métricas
│   ├── arbitrage/               # Lógica de arbitragem
│   ├── backtest/                # Backtest engine
│   ├── capital/                 # Gestão de capital
│   ├── execution/               # Execução de ordens
│   ├── exit/                    # Estratégia de saída
│   ├── fees/                    # Cálculo de taxas
│   ├── fetch/                   # Fetch de dados exchanges
│   ├── funding/                 # Funding rate
│   ├── history/                 # Histórico de trades
│   ├── kill_switch/             # Kill switch global
│   ├── market_data/             # Dados de mercado
│   ├── market_health/           # Saúde do mercado
│   ├── market_regime/           # Regime de mercado
│   ├── opportunity/             # Gestão de oportunidades
│   ├── paper/                   # Paper trading
│   ├── persistence/             # Persistência DB
│   ├── quality/                 # Quality scoring
│   ├── rebalance/               # Rebalanceamento
│   ├── risk/                    # Risk management
│   ├── scoring/                 # Scoring engine
│   ├── simulation/              # Simulações
│   ├── storage/                 # Storage de snapshots
│   └── trust/                   # Trust scoring
├── static/                      # Assets estáticos
├── templates/                   # Templates Jinja2
└── utils/
    ├── __init__.py
    ├── direction_helper.py      # Helpers de direção
    └── logging.py               # Config de logs
```

## 🔌 API Endpoints

### HTTP Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/health` | Health check v1 |
| `GET` | `/api/v1/opportunities` | Lista oportunidades |
| `GET` | `/api/v1/opportunities/{id}` | Detalhes da oportunidade |
| `GET` | `/api/v1/settings` | Configurações do usuário |
| `PUT` | `/api/v1/settings` | Atualiza configurações |
| `GET` | `/api/v1/pnl` | Registro de PnL |
| `GET` | `/api/v1/snapshots` | Pipeline snapshots |

### WebSocket Endpoints

| Endpoint | Descrição |
|----------|-----------|
| `WS /ws/opportunities` | Updates em tempo real |

## 🚀 Comandos

```bash
# Desenvolvimento
python src/backend/main.py

# Ou com uvicorn direto
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000

# Testes
pytest --cov=src/backend

# Code quality
black src/backend/ && flake8 src/backend/ && mypy src/backend/
```

## 📊 Database Schema

### Tabelas

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

## 🧪 Testes

```bash
# Rodar testes
pytest

# Com coverage
pytest --cov=src/backend --cov-report=html

# Testes específicos
pytest tests/test_opportunity_pipeline.py -v
```

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

## 📚 Documentação

- **Backend Spec:** `docs/specs/BACKEND-SPEC.md`
- **API Docs:** `http://localhost:8000/docs` (Swagger)
- **QA Spec:** `docs/specs/QA-SPEC.md`

---

**Versão:** 0.2.0
**Última atualização:** 2026-03-08
