/**
 * Hooks personalizados para DomCrypto Frontend
 * Seguindo FRONTEND-SPEC.md specification
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import type { OpportunityItemV2, SSEPayload, SSEMeta, FilterState, OpStatus, UserSettings, UpdateSettingsRequest, PnLRecord, PnLHistoryResponse } from '@/types'

// =============================================================================
// USE OPPORTUNITIES
// =============================================================================

interface UseOpportunitiesReturn {
  items: OpportunityItemV2[]
  meta: SSEMeta | null
  loading: boolean
  error: string | null
  isPaused: boolean
  setIsPaused: (paused: boolean) => void
  refresh: () => Promise<void>
}

export function useOpportunities(): UseOpportunitiesReturn {
  const [items, setItems] = useState<OpportunityItemV2[]>([])
  const [meta, setMeta] = useState<SSEMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isPaused, setIsPaused] = useState(false)

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch('/api/sse/opportunities')
      if (res.ok) {
        const data: SSEPayload = await res.json()
        setItems(data.items || [])
        setMeta(data.meta || null)
        setError(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (isPaused) return

    const eventSource = new EventSource('/api/sse/opportunities')

    eventSource.onmessage = (event) => {
      const data: SSEPayload = JSON.parse(event.data)
      setItems(data.items || [])
      setMeta(data.meta || null)
      setLoading(false)
      setError(null)
    }

    eventSource.onerror = () => {
      setError('Connection lost. Reconnecting...')
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [isPaused])

  // Initial fetch
  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 3000)
    return () => clearInterval(interval)
  }, [fetchData])

  return {
    items,
    meta,
    loading,
    error,
    isPaused,
    setIsPaused,
    refresh: fetchData
  }
}

// =============================================================================
// USE FILTERS
// =============================================================================

interface UseFiltersReturn extends FilterState {
  setMinSpread: (value: number) => void
  setMinScore: (value: number) => void
  setActiveSpots: (spots: string[]) => void
  setActiveFutures: (futures: string[]) => void
  setSearchTerm: (term: string) => void
  setStatusFilter: (status: OpStatus | 'all') => void
  toggleSpot: (spot: string) => void
  toggleFuture: (future: string) => void
  reset: () => void
  filterOpportunities: (opportunities: OpportunityItemV2[]) => OpportunityItemV2[]
}

const DEFAULT_FILTERS: FilterState = {
  minSpread: 0.5,
  minScore: 50,
  activeSpots: ['binance', 'mexc', 'bybit'],
  activeFutures: ['binance_futures', 'mexc_futures'],
  searchTerm: '',
  statusFilter: 'all',
  hideLowCapacity: false
}

export function useFilters(defaultFilters: Partial<FilterState> = {}): UseFiltersReturn {
  const [filters, setFilters] = useState<FilterState>({
    ...DEFAULT_FILTERS,
    ...defaultFilters
  })

  const setMinSpread = (value: number) => {
    setFilters(prev => ({ ...prev, minSpread: value }))
  }

  const setMinScore = (value: number) => {
    setFilters(prev => ({ ...prev, minScore: value }))
  }

  const setActiveSpots = (spots: string[]) => {
    setFilters(prev => ({ ...prev, activeSpots: spots }))
  }

  const setActiveFutures = (futures: string[]) => {
    setFilters(prev => ({ ...prev, activeFutures: futures }))
  }

  const setSearchTerm = (term: string) => {
    setFilters(prev => ({ ...prev, searchTerm: term }))
  }

  const setStatusFilter = (status: OpStatus | 'all') => {
    setFilters(prev => ({ ...prev, statusFilter: status }))
  }

  const toggleSpot = (spot: string) => {
    setFilters(prev => ({
      ...prev,
      activeSpots: prev.activeSpots.includes(spot)
        ? prev.activeSpots.filter(s => s !== spot)
        : [...prev.activeSpots, spot]
    }))
  }

  const toggleFuture = (future: string) => {
    setFilters(prev => ({
      ...prev,
      activeFutures: prev.activeFutures.includes(future)
        ? prev.activeFutures.filter(f => f !== future)
        : [...prev.activeFutures, future]
    }))
  }

  const reset = () => {
    setFilters({ ...DEFAULT_FILTERS })
  }

  const filterOpportunities = useMemo(() => {
    return (opportunities: OpportunityItemV2[]): OpportunityItemV2[] => {
      return opportunities.filter(opp => {
        // Search filter
        if (filters.searchTerm &&
            !opp.symbol.toLowerCase().includes(filters.searchTerm.toLowerCase())) {
          return false
        }

        // Spread filter
        if (opp.spread_net_pct < filters.minSpread) return false

        // Score filter
        if (opp.score < filters.minScore) return false

        // Exchange filters
        if (!filters.activeSpots.includes(opp.exchange_spot)) return false
        if (!filters.activeFutures.includes(opp.exchange_futures)) return false

        // Status filter
        if (filters.statusFilter !== 'all' && opp.status !== filters.statusFilter) {
          return false
        }

        // Capacity filter
        if (filters.hideLowCapacity && opp.capacity_band === 'RED') {
          return false
        }

        return true
      })
    }
  }, [filters])

  return {
    ...filters,
    setMinSpread,
    setMinScore,
    setActiveSpots,
    setActiveFutures,
    setSearchTerm,
    setStatusFilter,
    toggleSpot,
    toggleFuture,
    reset,
    filterOpportunities
  }
}

// =============================================================================
// USE SETTINGS
// =============================================================================

interface UseSettingsReturn {
  settings: UserSettings | null
  loading: boolean
  error: string | null
  updateSettings: (settings: UpdateSettingsRequest) => Promise<void>
  refresh: () => Promise<void>
}

export function useSettings(): UseSettingsReturn {
  const [settings, setSettings] = useState<UserSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSettings = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/settings')
      if (res.ok) {
        const data: UserSettings = await res.json()
        setSettings(data)
        setError(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch settings')
    } finally {
      setLoading(false)
    }
  }, [])

  const updateSettings = async (request: UpdateSettingsRequest) => {
    try {
      const res = await fetch('/api/v1/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      })
      if (res.ok) {
        const data: UserSettings = await res.json()
        setSettings(data)
        setError(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update settings')
      throw err
    }
  }

  useEffect(() => {
    fetchSettings()
  }, [fetchSettings])

  return {
    settings,
    loading,
    error,
    updateSettings,
    refresh: fetchSettings
  }
}

// =============================================================================
// USE PNL HISTORY
// =============================================================================

interface UsePnLHistoryReturn {
  items: PnLRecord[]
  total: number
  summary: { total_pnl_usd: number; trades_count: number }
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export function usePnLHistory(days: number = 30): UsePnLHistoryReturn {
  const [items, setItems] = useState<PnLRecord[]>([])
  const [total, setTotal] = useState(0)
  const [summary, setSummary] = useState({ total_pnl_usd: 0, trades_count: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPnL = useCallback(async () => {
    try {
      const res = await fetch(`/api/v1/pnl?days=${days}`)
      if (res.ok) {
        const data: PnLHistoryResponse = await res.json()
        setItems(data.items || [])
        setTotal(data.total)
        setSummary(data.summary)
        setError(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch PnL')
    } finally {
      setLoading(false)
    }
  }, [days])

  useEffect(() => {
    fetchPnL()
  }, [fetchPnL])

  return {
    items,
    total,
    summary,
    loading,
    error,
    refresh: fetchPnL
  }
}
