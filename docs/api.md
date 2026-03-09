# API Documentation

Documentação da API do DomCrypto.

## Backend Python (FastAPI)

### Endpoints

#### `GET /health`
Health check do serviço.

**Response:**
```json
{ "status": "healthy", "timestamp": "2026-03-08T12:00:00Z" }
```

#### `GET /api/v1/opportunities`
Lista oportunidades atuais.

**Query Params:**
- `min_spread`: Spread mínimo (%)
- `min_score`: Score mínimo
- `exchange`: Filtrar por exchange

**Response:**
```json
{
  "items": [
    {
      "id": "BTC-mexc-mexc_futures",
      "symbol": "BTC",
      "pair": "BTC/USDT",
      "exchange_spot": "mexc",
      "exchange_futures": "mexc_futures",
      "spread_exec_pct": 1.25,
      "spread_net_pct": 1.05,
      "roi_net_pct": 0.95,
      "score": 75,
      "status": "ACTIVE"
    }
  ],
  "meta": {
    "cycle_id": 1234,
    "ts": 1709899200,
    "counts": {
      "total": 50,
      "active": 12,
      "obs": 25,
      "killed": 13
    }
  }
}
```

#### `WS /ws/opportunities`
WebSocket para atualizações em tempo real.

**Connection:**
```python
ws = websocket.connect("ws://localhost:8000/ws/opportunities")
```

**Messages recebidas:**
```json
{
  "type": "opportunity_update",
  "data": {
    "items": [...],
    "meta": {...}
  }
}
```

### WebSocket Events

| Event | Descrição | Payload |
|-------|-----------|---------|
| `opportunity_new` | Nova oportunidade detectada | `OpportunityItemV2` |
| `opportunity_update` | Atualização de oportunidade existente | `OpportunityItemV2` |
| `opportunity_removed` | Oportunidade removida | `{ id: string }` |
| `pipeline_status` | Status do pipeline | `{ cycle_id, count, latency_ms }` |

---

## Frontend Next.js (API Routes)

### `GET /api/sse/opportunities`
Server-Sent Events para oportunidades.

**Headers:**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**Formato:**
```
data: {"items":[...],"meta":{...},"ts":1709899200}

```

### `GET /api/settings`
Obter configurações do usuário.

**Response:**
```json
{
  "profile_name": "default",
  "min_spread_pct": 0.5,
  "min_score": 50,
  "min_volume_usd": 100000,
  "bankroll_usd": 10000,
  "hedge_pct": 100,
  "allow_cross": true,
  "spots": ["binance", "mexc"],
  "futures": ["binance_futures", "mexc_futures"]
}
```

### `PUT /api/settings`
Atualizar configurações.

**Body:**
```json
{
  "min_spread_pct": 1.0,
  "min_score": 60,
  ...
}
```

---

## Tipos

### OpportunityItemV2

```typescript
interface OpportunityItemV2 {
  // Identidade
  id: string
  symbol: string
  pair: string
  exchange_spot: string
  exchange_futures: string
  is_cross_venue: boolean

  // Preços
  price_spot: number
  price_futures: number

  // Spread
  spread_exec_pct: number
  spread_net_pct: number

  // ROI e Capacidade
  roi_net_pct: number
  profit_usd: number
  capacity_pct: number
  capacity_band: 'GREEN' | 'YELLOW' | 'RED'
  entry_leg_usd: number

  // Liquidez
  spot_top_book_usd: number
  futures_top_book_usd: number
  volume_24h_usd: number

  // Funding
  funding_rate: number
  funding_interval_hours: number
  next_funding_at: number | null

  // Score e Status
  score: number
  trust_score: number
  status: 'ACTIVE' | 'READY' | 'OBSERVATION_ONLY' | 'KILLED'
  execution_decision: string

  // Meta
  persistence_minutes: number
  tags: string[]
  ts_created: number
  ts_updated: number
}
```

### UserSettings

```typescript
interface UserSettings {
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
