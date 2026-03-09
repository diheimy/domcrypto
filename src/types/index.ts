/**
 * Types TypeScript para DomCrypto Frontend
 * Seguindo FRONTEND-SPEC.md specification
 */

// =============================================================================
// CAPACITY & STATUS TYPES
// =============================================================================

export type CapacityBand = 'GREEN' | 'YELLOW' | 'RED'

export type OpStatus =
  | 'ACTIVE'
  | 'READY'
  | 'OBSERVATION_ONLY'
  | 'KILLED'
  | 'DEGRADED'

// =============================================================================
// OPPORTUNITY TYPES
// =============================================================================

/**
 * OpportunityItemV2 - Tipo principal de oportunidade
 * Segue especificação FRONTEND-SPEC.md
 */
export interface OpportunityItemV2 {
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
  capacity_band: CapacityBand
  entry_leg_usd: number

  // Liquidez
  spot_top_book_usd: number
  futures_top_book_usd: number
  volume_24h_usd: number

  // Funding
  funding_rate: number
  funding_interval_hours: number
  next_funding_at: number | null

  // Execução
  orders_to_fill_spot: number
  orders_to_fill_fut: number
  fill_status: string

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
  ts_created: number
  ts_updated: number
}

/**
 * Legacy DTO - Mantido para compatibilidade
 */
export interface OpportunityDTOv1 {
  id: string
  symbol: string
  exchange_spot: string
  exchange_futures: string
  spot_price: number
  futures_price: number
  spread_pct: number
  spread_net_pct: number
  volume_24h_usd: number
  score: number
  health_score: number
  tags: string[]
  status: string
  timestamp: string
}

// =============================================================================
// SSE & API TYPES
// =============================================================================

export interface SSEMeta {
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

export interface SSEPayload {
  items: OpportunityItemV2[]
  meta: SSEMeta
}

export interface OpportunitiesResponse {
  items: OpportunityItemV2[]
  meta: SSEMeta
}

export interface OpportunityDetailResponse {
  item: OpportunityItemV2
  exists: boolean
}

// =============================================================================
// USER SETTINGS TYPES
// =============================================================================

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

export interface UpdateSettingsRequest {
  profile_name?: string
  min_spread_pct?: number
  min_score?: number
  min_volume_usd?: number
  min_persistence_min?: number
  bankroll_usd?: number
  hedge_pct?: number
  entry_min_usd?: number
  entry_max_usd?: number
  hide_blocked?: boolean
  allow_cross?: boolean
  allow_same?: boolean
  spots?: string[]
  futures?: string[]
  blocked_coins?: string[]
}

// =============================================================================
// PnL TYPES
// =============================================================================

export type PnLStatus = 'OPEN' | 'CLOSED'

export interface PnLRecord {
  id: number
  symbol: string
  exchange_spot: string
  exchange_futures: string
  entry_at: string
  exit_at: string | null
  entry_spread: number
  exit_spread: number | null
  capital_usd: number
  pnl_usd: number | null
  pnl_pct: number | null
  fees_usd: number | null
  status: PnLStatus
  meta: Record<string, unknown> | null
}

export interface PnLHistoryResponse {
  items: PnLRecord[]
  total: number
  summary: {
    total_pnl_usd: number
    trades_count: number
  }
}

// =============================================================================
// PIPELINE SNAPSHOT TYPES
// =============================================================================

export interface PipelineSnapshot {
  id: number
  cycle_id: number
  ts: string
  count_raw: number
  count_active: number
  count_obs: number
  count_killed: number
  top_spread: number | null
  top_symbol: string | null
  meta: Record<string, unknown> | null
}

export interface PipelineSnapshotsResponse {
  items: PipelineSnapshot[]
  total: number
}

// =============================================================================
// HEALTH CHECK TYPES
// =============================================================================

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  timestamp: string
  version: string
  services: {
    pipeline: boolean
    database: boolean
    websocket: boolean
  }
}

// =============================================================================
// UI & FILTER TYPES
// =============================================================================

export interface FilterState {
  minSpread: number
  minScore: number
  activeSpots: string[]
  activeFutures: string[]
  searchTerm: string
  statusFilter: OpStatus | 'all'
  hideLowCapacity: boolean
}

export interface KPICard {
  title: string
  value: string | number
  change?: string
  trend?: 'up' | 'down' | 'neutral'
  icon: React.ReactNode
}
