/**
 * Utility functions para DomCrypto Frontend
 * Seguindo FRONTEND-SPEC.md specification
 */

// =============================================================================
// FORMATTERS
// =============================================================================

/**
 * Format number as USD currency
 */
export function formatUSD(value: number): string {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(2)}M`
  }
  if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}K`
  }
  return `$${value.toFixed(2)}`
}

/**
 * Format number as USD currency (alias for formatUSD)
 */
export function formatCurrency(value: number): string {
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(2)}M`
  }
  if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}K`
  }
  return `$${value.toFixed(2)}`
}

/**
 * Format percentage with sign
 */
export function formatPercent(value: number, decimals: number = 2): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(decimals)}%`
}

/**
 * Format number with K/M suffix
 */
export function formatNumber(value: number): string {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(2)}M`
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(0)}K`
  }
  return value.toFixed(0)
}

/**
 * Format timestamp to local time
 */
export function formatTime(timestamp: number): string {
  return new Date(timestamp * 1000).toLocaleTimeString()
}

/**
 * Format relative time (e.g., "5 min ago")
 */
export function formatRelativeTime(timestamp: number): string {
  const now = Date.now() / 1000
  const diff = now - timestamp

  if (diff < 60) return 'Agora'
  if (diff < 3600) return `${Math.floor(diff / 60)} min atrás`
  if (diff < 86400) return `${Math.floor(diff / 3600)} h atrás`
  return `${Math.floor(diff / 86400)} d atrás`
}

/**
 * Format funding rate
 */
export function formatFundingRate(rate: number): string {
  return `${(rate * 100).toFixed(4)}%`
}

// =============================================================================
// CLASS NAMES
// =============================================================================

/**
 * Merge class names conditionally
 */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ')
}

// =============================================================================
// CAPACITY BAND UTILS
// =============================================================================

import type { CapacityBand, OpStatus } from '@/types'

/**
 * Get capacity band color
 */
export function getCapacityColor(band: CapacityBand): string {
  switch (band) {
    case 'GREEN':
      return 'text-green bg-green/20'
    case 'YELLOW':
      return 'text-yellow-500 bg-yellow-500/20'
    case 'RED':
      return 'text-red bg-red/20'
    default:
      return 'text-muted bg-muted/20'
  }
}

/**
 * Get capacity band label
 */
export function getCapacityLabel(band: CapacityBand): string {
  return band
}

// =============================================================================
// STATUS UTILS
// =============================================================================

/**
 * Get status color
 */
export function getStatusColor(status: OpStatus): string {
  switch (status) {
    case 'ACTIVE':
    case 'READY':
      return 'text-green bg-green/20'
    case 'OBSERVATION_ONLY':
      return 'text-yellow-500 bg-yellow-500/20'
    case 'KILLED':
      return 'text-red bg-red/20'
    case 'DEGRADED':
      return 'text-muted bg-muted/20'
    default:
      return 'text-muted bg-muted/20'
  }
}

/**
 * Get status label
 */
export function getStatusLabel(status: OpStatus): string {
  switch (status) {
    case 'ACTIVE':
      return 'ACTIVE'
    case 'READY':
      return 'READY'
    case 'OBSERVATION_ONLY':
      return 'OBS'
    case 'KILLED':
      return 'KILLED'
    case 'DEGRADED':
      return 'DEGRADED'
    default:
      return status
  }
}

// =============================================================================
// SCORE UTILS
// =============================================================================

/**
 * Get score color based on value
 */
export function getScoreColor(score: number): string {
  if (score >= 70) return 'text-green'
  if (score >= 50) return 'text-yellow-500'
  return 'text-red'
}

/**
 * Get score background color
 */
export function getScoreBg(score: number): string {
  if (score >= 70) return 'bg-green/20'
  if (score >= 50) return 'bg-yellow-500/20'
  return 'bg-red/20'
}

/**
 * Get score quality level
 */
export function getScoreQuality(score: number): string {
  if (score >= 70) return 'HIGH'
  if (score >= 50) return 'MEDIUM'
  return 'LOW'
}

// =============================================================================
// EXCHANGE UTILS
// =============================================================================

/**
 * Get exchange display name
 */
export function getExchangeDisplayName(exchange: string): string {
  return exchange.replace('_futures', '').replace('_', ' ')
}

/**
 * Check if exchange is futures
 */
export function isFuturesExchange(exchange: string): boolean {
  return exchange.includes('_futures')
}

// =============================================================================
// VALIDATION
// =============================================================================

/**
 * Validate if opportunity is valid for display
 */
export function isValidOpportunity(opp: {
  spread_net_pct: number
  score: number
  volume_24h_usd: number
}): boolean {
  return (
    opp.spread_net_pct >= 0 &&
    opp.score >= 0 &&
    opp.score <= 100 &&
    opp.volume_24h_usd >= 0
  )
}
