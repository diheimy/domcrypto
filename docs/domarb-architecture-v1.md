# DomArb — Documento de Arquitetura v1.0

**Status:** Decisões fechadas. Pronto para implementação.
**Data:** 2026-03-01 | **Arquiteto:** Dom-Architect

---

## 1. Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        UBUNTU SERVER                            │
│                                                                 │
│  ┌─────────────────────┐      ┌──────────────────────────────┐ │
│  │   PYTHON SERVICE    │      │      NEXT.JS SERVICE         │ │
│  │   (FastAPI + UV)    │      │      (App Router + SSE)      │ │
│  │                     │      │                              │ │
│  │  OpportunityPipeline│      │  /app                        │ │
│  │  FetchService       │─WS──▶│  /api/sse/opportunities      │ │
│  │  QualityEngine      │      │  /api/settings               │ │
│  │  FundingEngine      │      │                              │ │
│  │  ExecutionEngine    │      │  Pages:                      │ │
│  │                     │      │  /dashboard                  │ │
│  │  :8000              │      │  /spot-futuros               │ │
│  └──────────┬──────────┘      │  /historico                  │ │
│             │                 │  /configuracoes              │ │
│             │ Prisma          │                              │ │
│             ▼ (writes)        │  :3000                       │ │
│  ┌─────────────────────┐      └──────────────┬───────────────┘ │
│  │     PostgreSQL      │◀─────────────────────┘               │
│  │                     │       Prisma (reads + writes)        │
│  │  opportunities      │                                      │
│  │  pipeline_snapshots │                                      │
│  │  user_settings      │                                      │
│  │  pnl_records        │                                      │
│  │  :5432              │                                      │
│  └─────────────────────┘                                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────── │
│  │              Docker Compose Network: domarb_net             │
│  └──────────────────────────────────────────────────────────── │
└─────────────────────────────────────────────────────────────────┘
                              │
                         SSE (HTTP)
                              │
                    ┌─────────▼──────────┐
                    │     BROWSER        │
                    │   React Client     │
                    │   EventSource API  │
                    └────────────────────┘
```

---

## 2. Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python, FastAPI, Pydantic |
| Frontend | Next.js 15 (App Router), TypeScript, React |
| Estilo | Tailwind CSS v4, ShadCN UI, Framer Motion, Lucide Icons |
| Banco de dados | PostgreSQL 16 + Prisma ORM |
| Real-time | SSE (browser) ← Next.js ← WebSocket ← Python |
| Fontes | Geist Sans (UI) + JetBrains Mono (dados numéricos) |
| Deploy | Docker Compose, Ubuntu Server |
| Auth MVP | Sem autenticação (acesso local/privado) |
| Cloud | Zero dependências externas |

---

## 3. Fluxo de Dados (End-to-End)

```
Python Pipeline (ciclo 3s)
         │
         │ 1. Processa oportunidades
         ▼
  op.to_adapter() ──▶ OpportunityItemV2 (projeção de 28 campos)
         │
         │ 2. Grava no PostgreSQL
         ▼
  INSERT INTO opportunities (id, payload, updated_at)
  ON CONFLICT (symbol, exchange_spot, exchange_futures)
  DO UPDATE SET payload = EXCLUDED.payload, updated_at = NOW()
         │
         │ 3. Notifica via NOTIFY
         ▼
  pg_notify('opportunities_channel', cycle_id)
         │
         ─────────────────────────────────────────────
         │
Next.js SSE Handler (/api/sse/opportunities)
         │
         │ 4. LISTEN opportunities_channel (pg client dedicado)
         │    OU polling fallback a cada 2s
         ▼
  SELECT * FROM opportunities
  WHERE updated_at > $last_seen
  ORDER BY score DESC
         │
         │ 5. Filtra por user_settings (spread, volume, exchanges)
         │    Aplica filtros server-side para reduzir payload
         ▼
  data: {"items": [...], "meta": {...}, "ts": 1234567890}\n\n
         │
         │ 6. EventSource no browser recebe
         ▼
  React state update ──▶ re-render da tabela (apenas diff)
```

> **Decisão crítica:** o `python-ws.ts` é um singleton de processo. Um único WebSocket conectado ao Python `:8000` recebe todos os ciclos e grava no PostgreSQL. O SSE handler lê do PostgreSQL, não do WebSocket diretamente. Isso desacopla os dois sistemas e garante que o histórico esteja sempre persistido independente de clientes conectados.

---

## 4. Schema do PostgreSQL

```sql
-- Tabela principal: estado atual de cada oportunidade
CREATE TABLE opportunities (
  symbol            VARCHAR(20)   NOT NULL,
  exchange_spot     VARCHAR(30)   NOT NULL,
  exchange_futures  VARCHAR(30)   NOT NULL,
  payload           JSONB         NOT NULL,   -- V2 contract completo
  score             SMALLINT      NOT NULL DEFAULT 0,
  spread_net_pct    DECIMAL(8,4)  NOT NULL DEFAULT 0,
  volume_24h_usd    BIGINT        NOT NULL DEFAULT 0,
  status            VARCHAR(20)   NOT NULL DEFAULT 'OBSERVATION_ONLY',
  capacity_band     VARCHAR(10)   NOT NULL DEFAULT 'RED',
  first_seen_at     TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  PRIMARY KEY (symbol, exchange_spot, exchange_futures)
);

CREATE INDEX idx_opp_score       ON opportunities(score DESC);
CREATE INDEX idx_opp_updated_at  ON opportunities(updated_at DESC);
CREATE INDEX idx_opp_status      ON opportunities(status);
CREATE INDEX idx_opp_payload_gin ON opportunities USING GIN(payload);

-- Snapshots do pipeline (histórico e análise)
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

CREATE INDEX idx_snap_ts ON pipeline_snapshots(ts DESC);

-- Configurações persistidas por perfil
CREATE TABLE user_settings (
  id            SERIAL        PRIMARY KEY,
  profile_name  VARCHAR(50)   NOT NULL DEFAULT 'default',
  settings      JSONB         NOT NULL,
  updated_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
  UNIQUE(profile_name)
);

-- Registro de PnL das operações executadas
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

CREATE INDEX idx_pnl_entry_at ON pnl_records(entry_at DESC);
CREATE INDEX idx_pnl_symbol   ON pnl_records(symbol);
```

> **Decisão de design:** `payload JSONB` no `opportunities` é intencional. O schema Python muda frequentemente (V113, V114…). Indexar só os campos usados em `WHERE`/`ORDER BY` e deixar o resto no JSONB elimina migrations a cada iteração do pipeline.

---

## 5. Contrato V2 (TypeScript)

```typescript
// types/opportunity.ts — fonte única de verdade no frontend

export type CapacityBand = 'GREEN' | 'YELLOW' | 'RED'
export type OpStatus =
  | 'ACTIVE'
  | 'READY'
  | 'OBSERVATION_ONLY'
  | 'KILLED'
  | 'DEGRADED'

export interface OpportunityItemV2 {
  // Identidade
  id: string
  symbol: string            // "BTC"
  pair: string              // "BTC/USDT"
  exchange_spot: string     // "mexc"
  exchange_futures: string  // "mexc_futures"
  is_cross_venue: boolean

  // Preços
  price_spot: number
  price_futures: number

  // Spread
  spread_exec_pct: number   // bruto — exibição
  spread_net_pct: number    // após fees — lógica de filtro

  // ROI e Capacidade
  roi_net_pct: number
  profit_usd: number
  capacity_pct: number
  capacity_band: CapacityBand
  entry_leg_usd: number

  // Liquidez
  spot_top_book_usd: number
  futures_top_book_usd: number
  volume_24h_usd: number

  // Funding
  funding_rate: number           // decimal: 0.0001 = 0.01%
  funding_interval_hours: number
  next_funding_at: number | null // unix timestamp

  // Execução
  orders_to_fill_spot: number
  orders_to_fill_fut: number
  fill_status: string
  spot_px_start: number
  spot_px_limit: number
  fut_px_start: number
  fut_px_limit: number

  // Score e Status
  score: number
  trust_score: number
  quality_level: string
  status: OpStatus
  execution_decision: string
  kill_reason: string | null

  // Meta
  persistence_minutes: number
  tags: string[]
  ts_created: number  // unix
  ts_updated: number  // unix
}

export interface SSEPayload {
  items: OpportunityItemV2[]
  meta: {
    cycle_id: number
    ts: number
    counts: {
      total: number
      active: number
      obs: number
      killed: number
    }
    pipeline_latency_ms: number
  }
}

export interface UserSettings {
  profile_name: string
  min_spread_pct: number
  min_score: number
  min_volume_usd: number
  min_persistence_min: number
  bankroll_usd: number
  hedge_pct: number
  entry_min_usd: number
  entry_max_usd: number
  hide_blocked: boolean
  allow_cross: boolean
  allow_same: boolean
  spots: string[]
  futures: string[]
  blocked_coins: string[]
}
```

---

## 6. Estrutura de Pastas (Next.js)

```
domarb-web/
├── app/
│   ├── layout.tsx                   # Root layout: sidebar + header
│   ├── page.tsx                     # Redirect → /dashboard
│   ├── dashboard/
│   │   └── page.tsx                 # KPIs globais
│   ├── spot-futuros/
│   │   └── page.tsx                 # Tabela de oportunidades (SSE)
│   ├── historico/
│   │   └── page.tsx                 # PnL records + pipeline snapshots
│   ├── configuracoes/
│   │   └── page.tsx                 # User settings form
│   └── api/
│       ├── sse/
│       │   └── opportunities/
│       │       └── route.ts         # SSE endpoint — consome WS Python
│       └── settings/
│           └── route.ts             # GET/PUT user_settings
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── AppShell.tsx
│   ├── opportunities/
│   │   ├── OpportunitiesTable.tsx   # Tabela principal
│   │   ├── OpportunityRow.tsx       # Linha renderizada
│   │   ├── ScoreBadge.tsx
│   │   ├── SpreadCell.tsx
│   │   ├── RoiCapacityCell.tsx      # ROI + banda de capacidade unificados
│   │   ├── ExchangeCell.tsx
│   │   ├── FundingCell.tsx
│   │   ├── StatusBadge.tsx
│   │   ├── TagList.tsx
│   │   └── ActionButtons.tsx
│   ├── filters/
│   │   ├── FilterDrawer.tsx         # Drawer lateral
│   │   ├── QualityFilters.tsx
│   │   ├── ExchangeFilters.tsx
│   │   └── CapitalFilters.tsx
│   ├── dashboard/
│   │   ├── KpiBar.tsx               # 5 cards de KPI
│   │   ├── KpiCard.tsx
│   │   └── PipelineStatus.tsx
│   └── ui/                          # ShadCN components (auto-gerados)
│
├── lib/
│   ├── prisma.ts                    # Prisma client singleton
│   ├── pg-notify.ts                 # PostgreSQL LISTEN/NOTIFY client
│   ├── python-ws.ts                 # WebSocket singleton → Python :8000
│   ├── sse-broadcaster.ts           # Gerencia conexões SSE ativas
│   └── settings.ts                  # CRUD user_settings
│
├── hooks/
│   ├── useOpportunities.ts          # Consome SSE, gerencia state
│   ├── useFilters.ts                # Filtros locais + sync com server
│   └── useSettings.ts              # Busca/salva settings
│
├── store/
│   └── opportunities.store.ts      # Zustand: state global das opps
│
├── types/
│   └── opportunity.ts               # Contratos TypeScript
│
├── prisma/
│   ├── schema.prisma
│   └── migrations/
│
├── docker-compose.yml
├── Dockerfile
└── .env.local
```

---

## 7. Docker Compose

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: domarb_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: domarb
      POSTGRES_USER: domarb
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - domarb_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U domarb"]
      interval: 5s
      timeout: 5s
      retries: 5

  python-backend:
    build:
      context: ./domarb-python
      dockerfile: Dockerfile
    container_name: domarb_python
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://domarb:${POSTGRES_PASSWORD}@postgres:5432/domarb
      PYTHONUNBUFFERED: "1"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - domarb_net
    ports:
      - "8000:8000"

  nextjs:
    build:
      context: ./domarb-web
      dockerfile: Dockerfile
    container_name: domarb_nextjs
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://domarb:${POSTGRES_PASSWORD}@postgres:5432/domarb
      PYTHON_WS_URL: ws://python-backend:8000/ws/opportunities
      NODE_ENV: production
    depends_on:
      - postgres
      - python-backend
    networks:
      - domarb_net
    ports:
      - "3000:3000"

networks:
  domarb_net:
    driver: bridge

volumes:
  postgres_data:
```

---

## 8. Design System

### Paleta de Cores

```css
@theme {
  --color-bg-base:      #000000;
  --color-bg-surface:   #060607;
  --color-bg-card:      #0f1319;
  --color-bg-hover:     #151a23;

  --color-border:       rgba(255,255,255,0.06);
  --color-border-gold:  rgba(252,213,53,0.25);

  --color-gold:         #FCD535;
  --color-gold-dim:     #f0b90b;
  --color-gold-glow:    rgba(252,213,53,0.15);

  --color-green:        #0ecb81;
  --color-red:          #f6465d;
  --color-blue:         #3b82f6;
  --color-muted:        #848e9c;

  --font-ui:            'Geist Sans', sans-serif;
  --font-mono:          'JetBrains Mono', monospace;
}
```

### Regras de Tipografia

- Valores numéricos (preços, spreads, percentuais) → `font-mono`
- Labels, títulos, navegação → `font-ui`
- Nunca misturar as duas fontes na mesma linha de dado

### Sidebar

- Largura: 240px fixo
- Fundo: `#000000` com borda direita `1px solid` gold dim
- Logo: centralizado no topo, altura máxima 120px
- Nav items: hover com background gold-glow + borda esquerda 3px gold
- Sem submenus colapsáveis no MVP

### Tabela de Oportunidades

**Modo Operacional (padrão — 9 colunas):**

```
Score | Ativo | Spread | ROI/Lucro | Exchanges | Volume | Funding | Status | Ação
```

**Modo Detalhado (toggle — +3 colunas):**

```
... + Faixa de Execução | Nº Ordens | Preço
```

### KPI Bar (Dashboard)

```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ OPORTUNIDADES│  MELHOR     │  SPREAD     │  VOLUME     │  SISTEMA    │
│   ATIVAS    │  SPREAD     │  MÉDIO      │  TOTAL 24H  │  STATUS     │
│     12      │  +2.34%     │  +0.87%     │  $4.2M      │  ● Online   │
│ 3 READY     │ BTC MEXC    │             │             │  3s delay   │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## 9. Tickets de Implementação

Sequência sem dependências circulares:

| # | Ticket | Entregável | Depende de |
|---|--------|-----------|------------|
| T1 | Infra Docker + PostgreSQL schema | `docker-compose.yml` + migrations Prisma | — |
| T2 | Python: Adapter V2 + pg_notify writer | `opportunity_ui_adapter.py` reescrito | T1 |
| T3 | Next.js: Scaffold + Design System | Estrutura de pastas + Tailwind tokens + fonts | T1 |
| T4 | Next.js: SSE Handler + python-ws singleton | `app/api/sse/opportunities/route.ts` | T2, T3 |
| T5 | Next.js: Tabela Spot x Futuros | `OpportunitiesTable` + cell components | T4 |
| T6 | Next.js: Dashboard KPIs | `KpiBar` + `PipelineStatus` | T4 |
| T7 | Next.js: Settings + Filter Drawer | `FilterDrawer` + `/api/settings` | T4 |
| T8 | Next.js: Histórico / PnL | Views de `pipeline_snapshots` + `pnl_records` | T4 |

**Ordem de execução:** T1 → T2 + T3 (paralelo) → T4 → T5 + T6 + T7 (paralelo) → T8

---

## 10. Decisões Arquiteturais Registradas

| Decisão | Escolha | Justificativa |
|---------|---------|---------------|
| Canal Python → Next.js | PostgreSQL NOTIFY + fallback poll | Zero acoplamento direto; histórico garantido mesmo sem clientes conectados |
| Schema `opportunities` | JSONB payload + colunas indexadas | Pipeline muda frequentemente; evita migrations contínuas |
| Real-time browser | SSE (EventSource) | Unidirecional, reconexão automática nativa, sem biblioteca adicional |
| WS Python | Singleton por processo Next.js | Evita multiplicar conexões ao Python por cliente SSE |
| Filtros | PostgreSQL + SSE sync | Persistência entre sessões sem necessidade de auth |
| Autenticação MVP | Sem auth | Acesso local/privado; reduz complexidade do MVP |
| Deploy | Docker Compose | Isolamento, reprodutibilidade, zero dependência do SO host |
| Banco de dados | PostgreSQL local | Zero cloud; NOTIFY/LISTEN nativo; JSONB indexável |
