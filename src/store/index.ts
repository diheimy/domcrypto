/**
 * Zustand Store para oportunidades
 * Seguindo FRONTEND-SPEC.md specification
 */

import { create } from 'zustand'
import type { OpportunityItemV2, SSEMeta } from '@/types'

interface OpportunitiesState {
  // State
  items: OpportunityItemV2[]
  meta: SSEMeta | null
  loading: boolean
  error: string | null

  // Actions
  setOpportunities: (items: OpportunityItemV2[]) => void
  setMeta: (meta: SSEMeta) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clear: () => void
  updateItem: (id: string, updates: Partial<OpportunityItemV2>) => void
  removeItem: (id: string) => void
}

export const useOpportunitiesStore = create<OpportunitiesState>((set) => ({
  // Initial state
  items: [],
  meta: null,
  loading: true,
  error: null,

  // Actions
  setOpportunities: (items) => set({ items, loading: false }),
  setMeta: (meta) => set({ meta }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
  clear: () => set({ items: [], meta: null, loading: false, error: null }),

  updateItem: (id, updates) => set((state) => ({
    items: state.items.map((item) =>
      item.id === id ? { ...item, ...updates } : item
    )
  })),

  removeItem: (id) => set((state) => ({
    items: state.items.filter((item) => item.id !== id)
  }))
}))

// =============================================================================
// SETTINGS STORE
// =============================================================================

import type { UserSettings } from '@/types'

interface SettingsState {
  // State
  settings: UserSettings | null
  loading: boolean
  error: string | null

  // Actions
  setSettings: (settings: UserSettings) => void
  updateSettings: (updates: Partial<UserSettings>) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

const DEFAULT_SETTINGS: UserSettings = {
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
  spots: ['binance', 'mexc', 'bybit'],
  futures: ['binance_futures', 'mexc_futures'],
  blocked_coins: []
}

export const useSettingsStore = create<SettingsState>((set) => ({
  // Initial state
  settings: DEFAULT_SETTINGS,
  loading: false,
  error: null,

  // Actions
  setSettings: (settings) => set({ settings, error: null }),
  updateSettings: (updates) => set((state) => ({
    settings: state.settings ? { ...state.settings, ...updates } : null
  })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false })
}))

// =============================================================================
// FILTER STORE
// =============================================================================

import type { FilterState } from '@/types'

interface FilterStateStore extends Omit<FilterState, 'filterOpportunities'> {
  // Actions
  setMinSpread: (value: number) => void
  setMinScore: (value: number) => void
  setActiveSpots: (spots: string[]) => void
  setActiveFutures: (futures: string[]) => void
  setSearchTerm: (term: string) => void
  toggleSpot: (spot: string) => void
  toggleFuture: (future: string) => void
  reset: () => void
}

const DEFAULT_FILTERS: Omit<FilterState, 'filterOpportunities'> = {
  minSpread: 0.5,
  minScore: 50,
  activeSpots: ['binance', 'mexc', 'bybit'],
  activeFutures: ['binance_futures', 'mexc_futures'],
  searchTerm: '',
  statusFilter: 'all',
  hideLowCapacity: false
}

export const useFiltersStore = create<FilterStateStore>((set) => ({
  // Initial state
  ...DEFAULT_FILTERS,

  // Actions
  setMinSpread: (value) => set({ minSpread: value }),
  setMinScore: (value) => set({ minScore: value }),
  setActiveSpots: (spots) => set({ activeSpots: spots }),
  setActiveFutures: (futures) => set({ activeFutures: futures }),
  setSearchTerm: (term) => set({ searchTerm: term }),

  toggleSpot: (spot) => set((state) => ({
    activeSpots: state.activeSpots.includes(spot)
      ? state.activeSpots.filter(s => s !== spot)
      : [...state.activeSpots, spot]
  })),

  toggleFuture: (future) => set((state) => ({
    activeFutures: state.activeFutures.includes(future)
      ? state.activeFutures.filter(f => f !== future)
      : [...state.activeFutures, future]
  })),

  reset: () => set({ ...DEFAULT_FILTERS })
}))
