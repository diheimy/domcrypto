/**
 * Constants para DomCrypto Frontend
 * Seguindo FRONTEND-SPEC.md specification
 */

// =============================================================================
// EXCHANGES
// =============================================================================

export const SUPPORTED_SPOT_EXCHANGES = [
  'binance',
  'mexc',
  'bybit',
  'gate',
  'bitget',
  'bingx'
] as const

export const SUPPORTED_FUTURES_EXCHANGES = [
  'binance_futures',
  'mexc_futures',
  'bybit_futures',
  'gate_futures',
  'bitget_futures',
  'bingx_futures'
] as const

export const EXCHANGE_LABELS: Record<string, string> = {
  binance: 'Binance',
  mexc: 'MEXC',
  bybit: 'Bybit',
  gate: 'Gate.io',
  bitget: 'Bitget',
  bingx: 'BingX',
  binance_futures: 'Binance Futures',
  mexc_futures: 'MEXC Futures',
  bybit_futures: 'Bybit Futures',
  gate_futures: 'Gate Futures',
  bitget_futures: 'Bitget Futures',
  bingx_futures: 'BingX Futures'
}

// =============================================================================
// FILTERS
// =============================================================================

export const DEFAULT_FILTERS = {
  minSpread: 0.5,
  minScore: 50,
  minVolumeUsd: 100000,
  minPersistenceMin: 0
} as const

export const FILTER_PRESETS = {
  conservative: {
    minSpread: 1.0,
    minScore: 70,
    minVolumeUsd: 500000
  },
  moderate: {
    minSpread: 0.5,
    minScore: 50,
    minVolumeUsd: 100000
  },
  aggressive: {
    minSpread: 0.2,
    minScore: 30,
    minVolumeUsd: 50000
  }
} as const

// =============================================================================
// SETTINGS
// =============================================================================

export const DEFAULT_SETTINGS = {
  profile_name: 'default',
  min_spread_pct: 0.5,
  min_score: 50,
  min_volume_usd: 100000,
  min_persistence_min: 0,
  bankroll_usd: 10000,
  hedge_pct: 100,
  entry_min_usd: 100,
  entry_max_usd: 1000,
  hide_blocked: false,
  allow_cross: true,
  allow_same: true,
  spots: SUPPORTED_SPOT_EXCHANGES,
  futures: SUPPORTED_FUTURES_EXCHANGES,
  blocked_coins: []
} as const

// =============================================================================
// STATUS
// =============================================================================

export const STATUS_LABELS: Record<string, string> = {
  ACTIVE: 'Active',
  READY: 'Ready',
  OBSERVATION_ONLY: 'Observation',
  KILLED: 'Killed',
  DEGRADED: 'Degraded'
} as const

export const STATUS_COLORS: Record<string, string> = {
  ACTIVE: 'bg-green/20 text-green',
  READY: 'bg-blue/20 text-blue',
  OBSERVATION_ONLY: 'bg-yellow-500/20 text-yellow-500',
  KILLED: 'bg-red/20 text-red',
  DEGRADED: 'bg-muted/20 text-muted'
} as const

// =============================================================================
// CAPACITY
// =============================================================================

export const CAPACITY_LABELS: Record<string, string> = {
  GREEN: 'High Capacity',
  YELLOW: 'Medium Capacity',
  RED: 'Low Capacity'
} as const

export const CAPACITY_COLORS: Record<string, string> = {
  GREEN: 'bg-green/20 text-green',
  YELLOW: 'bg-yellow-500/20 text-yellow-500',
  RED: 'bg-red/20 text-red'
} as const

// =============================================================================
// TIME
// =============================================================================

export const FUNDING_INTERVALS = {
  1: '1 hour',
  4: '4 hours',
  8: '8 hours',
  12: '12 hours',
  24: '24 hours'
} as const

export const REFRESH_INTERVAL_MS = 3000 // 3 seconds
export const SSE_RECONNECT_INTERVAL_MS = 5000 // 5 seconds

// =============================================================================
// UI
// =============================================================================

export const UI_CONSTANTS = {
  tablePageSize: 50,
  kpiUpdateInterval: 1000,
  toastDuration: 5000,
  animationDuration: 200
} as const

// =============================================================================
// VALIDATION
// =============================================================================

export const VALIDATION_RULES = {
  minSpread: { min: 0, max: 10, step: 0.1 },
  minScore: { min: 0, max: 100, step: 5 },
  minVolume: { min: 0, max: 10000000, step: 10000 }
} as const
