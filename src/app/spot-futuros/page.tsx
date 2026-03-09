'use client'

import { useState, useMemo } from 'react'
import { Filter, Pause, Play, AlertCircle } from 'lucide-react'

// Types
import type { OpportunityItemV2, UserSettings } from '@/types'

// Hooks
import { useOpportunities } from '@/hooks'
import { useFilters } from '@/hooks'

// Components
import { KpiBar } from '@/components/dashboard/KpiBar'
import { OpportunitiesTable } from '@/components/opportunities/OpportunitiesTable'
import {
  FilterDrawer,
  ExchangeFilter,
  SpreadFilter,
  ScoreFilter,
  SearchFilter
} from '@/components/filters'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'

// Constants
import { SUPPORTED_SPOT_EXCHANGES, SUPPORTED_FUTURES_EXCHANGES } from '@/utils/constants'

// Utils
import { cn } from '@/utils/formatters'

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

export default function SpotFuturosPage() {
  const {
    items: opportunities,
    meta,
    loading,
    error,
    isPaused,
    setIsPaused
  } = useOpportunities()

  const filters = useFilters({
    minSpread: DEFAULT_SETTINGS.min_spread_pct,
    minScore: DEFAULT_SETTINGS.min_score
  })

  const [showFilters, setShowFilters] = useState(false)
  const [hideRedCapacity, setHideRedCapacity] = useState(false)

  // Filter opportunities
  const filteredOpps = useMemo(() => {
    return filters.filterOpportunities(opportunities).filter(opp => {
      if (hideRedCapacity && opp.capacity_band === 'RED') return false
      if (DEFAULT_SETTINGS.blocked_coins.includes(opp.symbol)) return false
      return true
    })
  }, [opportunities, filters, hideRedCapacity])

  // KPI calculations
  const activeOpps = filteredOpps.filter(o => o.status === 'ACTIVE').length
  const bestSpread = filteredOpps.length > 0
    ? Math.max(...filteredOpps.map(o => o.spread_net_pct))
    : 0
  const avgSpread = filteredOpps.length > 0
    ? filteredOpps.reduce((acc, o) => acc + o.spread_net_pct, 0) / filteredOpps.length
    : 0

  // Handlers
  const handleViewDetails = (_opp: OpportunityItemV2) => {
    void 'View details'
    // TODO: Open details modal
  }

  const handleExecute = (_opp: OpportunityItemV2) => {
    void 'Execute'
    // TODO: Execute trade
  }

  const handleKill = (_opp: OpportunityItemV2) => {
    void 'Kill'
    // TODO: Kill opportunity
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-gold border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted">Carregando oportunidades...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 lg:p-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-white mb-1">Spot x Futuros</h1>
          <p className="text-muted text-sm">Intelligence - Oportunidades em tempo real</p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant={isPaused ? 'secondary' : 'primary'}
            size="sm"
            onClick={() => setIsPaused(!isPaused)}
            className="min-w-[120px]"
          >
            {isPaused ? <Play size={18} /> : <Pause size={18} />}
            <span className="hidden sm:inline ml-2">{isPaused ? 'Pausado' : 'Executando'}</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(true)}
            className={cn(showFilters && 'border-gold text-gold')}
          >
            <Filter size={18} />
            <span className="hidden sm:inline ml-2">Filtros</span>
          </Button>
        </div>
      </div>

      {/* KPI Bar */}
      <KpiBar
        activeOpportunities={activeOpps}
        bestSpread={bestSpread}
        avgSpread={avgSpread}
        pipelineLatencyMs={meta?.pipeline_latency_ms || 0}
      />

      {/* Filter Drawer */}
      <FilterDrawer
        isOpen={showFilters}
        onClose={() => setShowFilters(false)}
        onReset={filters.reset}
      >
        <div className="space-y-6">
          {/* Search */}
          <SearchFilter
            value={filters.searchTerm}
            onChange={filters.setSearchTerm}
          />

          {/* Spread Filter */}
          <SpreadFilter
            value={filters.minSpread}
            onChange={filters.setMinSpread}
          />

          {/* Score Filter */}
          <ScoreFilter
            value={filters.minScore}
            onChange={filters.setMinScore}
          />

          {/* Spot Exchanges */}
          <ExchangeFilter
            title="Exchanges Spot"
            exchanges={[...SUPPORTED_SPOT_EXCHANGES]}
            activeExchanges={filters.activeSpots}
            onToggle={filters.toggleSpot}
          />

          {/* Futures Exchanges */}
          <ExchangeFilter
            title="Exchanges Futuros"
            exchanges={[...SUPPORTED_FUTURES_EXCHANGES]}
            activeExchanges={filters.activeFutures}
            onToggle={filters.toggleFuture}
          />

          {/* Additional Options */}
          <div className="pt-4 border-t border-border">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-muted">Esconder Capacidade RED</span>
              <Switch
                checked={hideRedCapacity}
                onChange={(e) => setHideRedCapacity(e.target.checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted">Permitir Cross-venue</span>
              <Switch
                checked={DEFAULT_SETTINGS.allow_cross}
                readOnly
              />
            </div>
          </div>
        </div>
      </FilterDrawer>

      {/* Opportunities Table */}
      <div className="glass rounded-xl border border-border overflow-hidden">
        <OpportunitiesTable
          data={filteredOpps}
          onViewDetails={handleViewDetails}
          onExecute={handleExecute}
          onKill={handleKill}
          sortBy="spread"
          sortOrder="desc"
        />
      </div>

      {/* Footer info */}
      <div className="mt-4 flex items-center justify-between text-xs text-muted">
        <div className="flex items-center gap-4">
          <span>Total: {filteredOpps.length} oportunidades</span>
          <span>|</span>
          <span>Cycle: #{meta?.cycle_id || 0}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className={cn(
            'w-2 h-2 rounded-full animate-pulse',
            meta ? 'bg-green' : 'bg-red'
          )} />
          <span>{meta ? 'Dados atualizados' : 'Aguardando dados...'}</span>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="fixed bottom-4 right-4 glass rounded-xl p-4 border border-red/50 max-w-sm">
          <div className="flex items-start gap-3">
            <AlertCircle size={20} className="text-red mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-white">Erro de conexão</h4>
              <p className="text-xs text-muted mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
