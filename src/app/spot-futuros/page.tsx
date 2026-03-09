'use client'

import { useState, useMemo, useCallback, useEffect } from 'react'
import { AlertCircle, Filter, Settings, RotateCcw, Search, Pause, Play, Eye, Play as PlayIcon, X } from 'lucide-react'
import './spot-futuros.css'

// Types
import type { OpportunityItemV2, UserSettings } from '@/types'

// Hooks
import { useOpportunities } from '@/hooks'
import { useFilters } from '@/hooks'

// Constants
import { SUPPORTED_SPOT_EXCHANGES, SUPPORTED_FUTURES_EXCHANGES } from '@/utils/constants'

// Utils
import { cn, formatUSD } from '@/utils/formatters'

// Force dynamic rendering para evitar erro de window no SSR
export const dynamic = 'force-dynamic'

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

type SortKey = 'score' | 'spread' | 'volume' | 'capacity' | 'status'
type SortDir = 'asc' | 'desc'

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
  const [sortConfig, setSortConfig] = useState<{ key: SortKey; dir: SortDir }>({ key: 'score', dir: 'desc' })
  const [searchTerm, setSearchTerm] = useState('')

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K para search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        const searchInput = document.querySelector('.search-box input') as HTMLInputElement
        searchInput?.focus()
      }
      // Cmd/Ctrl + F para filters
      if ((e.metaKey || e.ctrlKey) && e.key === 'f') {
        e.preventDefault()
        setShowFilters(prev => !prev)
      }
      // Escape para fechar filtros
      if (e.key === 'Escape') {
        setShowFilters(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Filter opportunities
  const filteredOpps = useMemo(() => {
    let result = filters.filterOpportunities(opportunities)

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(opp => opp.symbol.toLowerCase().includes(term))
    }

    // Hide red capacity
    if (hideRedCapacity) {
      result = result.filter(opp => opp.capacity_band !== 'RED')
    }

    // Sort
    result = [...result].sort((a, b) => {
      let comparison = 0
      switch (sortConfig.key) {
        case 'score': comparison = b.score - a.score; break
        case 'spread': comparison = b.spread_net_pct - a.spread_net_pct; break
        case 'volume': comparison = b.volume_24h_usd - a.volume_24h_usd; break
        case 'capacity': comparison = (b.capacity_pct || 0) - (a.capacity_pct || 0); break
        case 'status': comparison = a.status.localeCompare(b.status); break
      }
      return sortConfig.dir === 'desc' ? comparison : -comparison
    })

    return result
  }, [opportunities, filters, hideRedCapacity, searchTerm, sortConfig])

  // KPI calculations
  const activeOpps = filteredOpps.filter(o => o.status === 'ACTIVE').length
  const readyOpps = filteredOpps.filter(o => o.status === 'READY').length

  // Get current profile
  const getCurrentProfile = () => {
    if (filters.minSpread >= 1.0 && filters.minScore >= 70) return 'conservador'
    if (filters.minSpread >= 0.5 && filters.minScore >= 50) return 'moderado'
    return 'agressivo'
  }

  // Get coin initial color based on symbol
  const getCoinColor = (symbol: string) => {
    const colors = ['#F59E0B', '#3B82F6', '#10B981', '#EF4444', '#8B5CF6', '#EC4899']
    const index = symbol.charCodeAt(0) % colors.length
    return colors[index]
  }

  // Handlers
  const handleSort = (key: SortKey) => {
    setSortConfig(prev => ({
      key,
      dir: prev.key === key && prev.dir === 'desc' ? 'asc' : 'desc'
    }))
  }

  const handleViewDetails = useCallback((opp: OpportunityItemV2) => {
    // TODO: Implement details modal
    // eslint-disable-next-line no-console
    console.log('View details:', opp)
  }, [])

  const handleExecute = useCallback((opp: OpportunityItemV2) => {
    // TODO: Implement execution flow
    // eslint-disable-next-line no-console
    console.log('Execute:', opp)
  }, [])

  const handleKill = useCallback((opp: OpportunityItemV2) => {
    // TODO: Implement kill functionality
    // eslint-disable-next-line no-console
    console.log('Kill:', opp)
  }, [])

  const getScoreClass = (score: number, status: string) => {
    if (status === 'READY') return 'score-badge score-ready'
    if (score >= 70) return 'score-badge score-ready'
    if (score >= 50) return 'score-badge score-watch'
    return 'score-badge score-lowqual'
  }

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'status-badge status-active'
      case 'READY': return 'status-badge status-ready'
      case 'KILLED': return 'status-badge status-killed'
      default: return 'status-badge status-observation'
    }
  }

  const getCapacityClass = (band: string) => {
    switch (band) {
      case 'GREEN': return 'col-capacity cap-max'
      case 'YELLOW': return 'col-capacity cap-med'
      case 'RED': return 'col-capacity cap-min'
      default: return 'col-capacity cap-none'
    }
  }

  const renderTags = (tags: string[]) => {
    if (!tags || tags.length === 0) return null

    const severityOrder = { trap: 0, warn: 1, good: 2, info: 3 }
    const getSeverity = (tag: string) => {
      const t = tag.toUpperCase()
      if (t.includes('INVALID') || t.includes('FAIL') || t.includes('TRAP') || t.includes('NEGATIVE')) return 'trap'
      if (t.includes('FEE') || t.includes('THIN') || t.includes('NO_DEPTH')) return 'warn'
      if (t.includes('REAL') || t.includes('STRONG') || t.includes('SOLID')) return 'good'
      return 'info'
    }

    const sorted = [...tags].sort((a, b) =>
      severityOrder[getSeverity(a) as keyof typeof severityOrder] -
      severityOrder[getSeverity(b) as keyof typeof severityOrder]
    )

    const maxTags = 6
    const visible = sorted.slice(0, maxTags)
    const hidden = sorted.slice(maxTags)

    return (
      <div className="tag-grid">
        {visible.map((tag, i) => {
          const severity = getSeverity(tag)
          const shortTag = tag.replace(/_/g, '').slice(0, 4).padEnd(4, 'X')
          return (
            <span
              key={i}
              className={cn(`tag sev-${severity}`, `tag-${tag}`)}
              title={tag}
            >
              {shortTag}
            </span>
          )
        })}
        {hidden.length > 0 && (
          <span className="tag sev-info" title={hidden.join(', ')}>
            +{hidden.length}
          </span>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--bg-primary)' }}>
        <div className="text-center">
          <div className="loading-container">
            <div className="loading-spinner" />
            <span className="loading-text">Carregando oportunidades...</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 lg:p-6" style={{ background: 'var(--bg-primary)', minHeight: '100vh' }}>
      {/* Header Stats */}
      <div className="stats-grid mb-4">
        <div className="stat-val text-green">
          <span className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 bg-green rounded-full animate-pulse" />
            <span>Sistema Online -</span>
          </span>
          <span style={{ color: '#94A3B8', fontWeight: 300, marginLeft: 4, fontSize: 12 }}>
            Última:{' '}
          </span>
          <span style={{ fontSize: 10, color: '#F59E0B', marginLeft: 2, fontFamily: 'monospace' }}>
            {meta?.ts ? new Date(meta.ts).toLocaleTimeString() : '--:--:--'}
          </span>
        </div>
      </div>

      {/* Toolbar */}
      <div className="toolbar">
        <div className="tool-header">
          <div>
            <div className="stat-val text-green" style={{ fontSize: 14 }}>Oportunidades</div>
            <div style={{ fontSize: 12, color: '#888' }}>
              <span id="opp-count" style={{ color: '#FFFFFF', fontWeight: 700 }}>
                {filteredOpps.length}
              </span>{' '}
              pares ativos
            </div>
          </div>

          <div className="right-controls">
            <div className="search-box">
              <Search size={14} style={{ color: '#888' }} />
              <input
                type="text"
                placeholder="Ativo..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <button
              className="btn-filter-toggle"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter size={14} /> Filtros
            </button>

            <button
              className="btn-action"
              onClick={() => setShowFilters(!showFilters)}
              title="Configurações"
            >
              <Settings size={14} />
            </button>

            <button
              className="btn-action"
              onClick={() => setIsPaused(!isPaused)}
              title={isPaused ? 'Retomar' : 'Pausar'}
            >
              {isPaused ? <Play size={14} /> : <Pause size={14} />}
            </button>

            <button
              className="btn-action"
              onClick={() => {
                filters.reset()
                setSearchTerm('')
              }}
              title="Resetar"
            >
              <RotateCcw size={14} />
            </button>
          </div>
        </div>

        {/* Filter Summary Bar */}
        <div className="filter-summary-bar">
          <span>Perfil:</span>
          <span className={cn('profile-tag', `prof-${getCurrentProfile()}`)}>
            {getCurrentProfile()}
          </span>
          <span style={{ margin: '0 8px' }}>|</span>
          <span>Spread Mín:</span>
          <span className="summary-value">{filters.minSpread.toFixed(2)}%</span>
          <span style={{ margin: '0 8px' }}>|</span>
          <span>Score Mín:</span>
          <span className="summary-value">{filters.minScore}</span>
          <span style={{ margin: '0 8px' }}>|</span>
          <span>Spot:</span>
          <span className="summary-value">{filters.activeSpots.length}</span>
          <span style={{ margin: '0 8px' }}>|</span>
          <span>Futuros:</span>
          <span className="summary-value">{filters.activeFutures.length}</span>
        </div>

        {/* Filter Panel */}
        {showFilters && (
          <div className="filter-expanded-area active">
            <div className="filter-grid">
              {/* Column 1: Quality Config */}
              <div className="filter-col">
                <h4>Configuração de Qualidade</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 5 }}>
                  <div className="input-group">
                    <label>Spread Min (%):</label>
                    <input
                      type="number"
                      className="filter-input"
                      step="0.1"
                      value={filters.minSpread}
                      onChange={(e) => filters.setMinSpread(Number(e.target.value))}
                    />
                  </div>
                  <div className="input-group">
                    <label>Score Mínimo:</label>
                    <input
                      type="number"
                      className="filter-input"
                      step="10"
                      value={filters.minScore}
                      onChange={(e) => filters.setMinScore(Number(e.target.value))}
                    />
                  </div>
                  <div className="input-group">
                    <label>Persistência (min):</label>
                    <input
                      type="number"
                      className="filter-input"
                      step="1"
                      value="0"
                      readOnly
                    />
                  </div>
                  <div className="input-group">
                    <label>Vol 24h Mín ($):</label>
                    <input
                      type="number"
                      className="filter-input"
                      value="50000"
                      step="10000"
                      readOnly
                    />
                  </div>
                </div>
                <div className="input-group" style={{ marginTop: 8 }}>
                  <label>Perfil:</label>
                  <div className="profile-btns">
                    <button
                      className={cn('btn-profile', 'prof-green')}
                      onClick={() => {
                        filters.setMinSpread(1.0)
                        filters.setMinScore(70)
                      }}
                    >
                      Conservador
                    </button>
                    <button
                      className={cn('btn-profile', 'prof-yellow')}
                      onClick={() => {
                        filters.setMinSpread(0.5)
                        filters.setMinScore(50)
                      }}
                    >
                      Moderado
                    </button>
                    <button
                      className={cn('btn-profile', 'prof-red')}
                      onClick={() => {
                        filters.setMinSpread(0.2)
                        filters.setMinScore(30)
                      }}
                    >
                      Agressivo
                    </button>
                  </div>
                </div>
              </div>

              {/* Column 2: Spot Exchanges */}
              <div className="filter-col">
                <h4>Corretoras Spot</h4>
                <div className="exch-list">
                  {SUPPORTED_SPOT_EXCHANGES.map((ex) => (
                    <div
                      key={ex}
                      className={cn('exch-check', filters.activeSpots.includes(ex) && 'checked')}
                      onClick={() => filters.toggleSpot(ex)}
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={`https://assets.coincap.io/assets/icons/${ex}@2x.png`} alt={ex} />
                      {ex.toUpperCase()}
                    </div>
                  ))}
                </div>
              </div>

              {/* Column 3: Futures Exchanges */}
              <div className="filter-col">
                <h4>Corretoras Futuros</h4>
                <div className="exch-list">
                  {SUPPORTED_FUTURES_EXCHANGES.map((ex) => (
                    <div
                      key={ex}
                      className={cn('exch-check', filters.activeFutures.includes(ex) && 'checked')}
                      onClick={() => filters.toggleFuture(ex)}
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={`https://assets.coincap.io/assets/icons/${ex.replace('_futures', '')}@2x.png`} alt={ex} />
                      {ex.replace('_futures', '').toUpperCase()}
                    </div>
                  ))}
                </div>
              </div>

              {/* Column 4: Options */}
              <div className="filter-col">
                <h4>Opções Adicionais</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <label style={{ fontSize: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <input
                      type="checkbox"
                      checked={hideRedCapacity}
                      onChange={(e) => setHideRedCapacity(e.target.checked)}
                    />
                    Esconder Capacidade RED
                  </label>
                  <label style={{ fontSize: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <input
                      type="checkbox"
                      checked={DEFAULT_SETTINGS.allow_cross}
                      readOnly
                    />
                    Permitir Cross-venue
                  </label>
                  <label style={{ fontSize: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <input
                      type="checkbox"
                      checked={DEFAULT_SETTINGS.allow_same}
                      readOnly
                    />
                    Permitir Same-venue
                  </label>
                </div>
              </div>
            </div>

            <div className="filter-actions">
              <button className="btn-cancel" onClick={() => setShowFilters(false)}>
                Fechar
              </button>
              <button className="btn-apply" onClick={() => setShowFilters(false)}>
                Aplicar Filtros
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Sort Indicator */}
      <div className="sort-indicator">
        Ordenado por:{' '}
        <span className="sort-indicator-key">
          {sortConfig.key === 'score' ? 'Score' :
           sortConfig.key === 'spread' ? 'Spread' :
           sortConfig.key === 'volume' ? 'Volume' :
           sortConfig.key === 'capacity' ? 'Capacidade' : 'Status'}
        </span>{' '}
        ({sortConfig.dir === 'desc' ? 'decrescente' : 'crescente'})
      </div>

      {/* Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th
                className={cn('sortable', sortConfig.key === 'score' && 'active-sort')}
                onClick={() => handleSort('score')}
              >
                <span className="th-label">Score</span>
                <span className="sort-arrow">{sortConfig.key === 'score' ? (sortConfig.dir === 'desc' ? '▼' : '▲') : '↕'}</span>
              </th>
              <th><span className="th-label">Ativo</span></th>
              <th
                className={cn('sortable', sortConfig.key === 'spread' && 'active-sort')}
                onClick={() => handleSort('spread')}
              >
                <span className="th-label">Spread</span>
                <span className="sort-arrow">{sortConfig.key === 'spread' ? (sortConfig.dir === 'desc' ? '▼' : '▲') : '↕'}</span>
              </th>
              <th
                className={cn('sortable', sortConfig.key === 'volume' && 'active-sort')}
                onClick={() => handleSort('volume')}
              >
                <span className="th-label">Volume 24h</span>
                <span className="sort-arrow">{sortConfig.key === 'volume' ? (sortConfig.dir === 'desc' ? '▼' : '▲') : '↕'}</span>
              </th>
              <th
                className={cn('sortable', sortConfig.key === 'capacity' && 'active-sort')}
                onClick={() => handleSort('capacity')}
              >
                <span className="th-label">Capacidade</span>
                <span className="sort-arrow">{sortConfig.key === 'capacity' ? (sortConfig.dir === 'desc' ? '▼' : '▲') : '↕'}</span>
              </th>
              <th><span className="th-label">Exchanges</span></th>
              <th><span className="th-label">Preço Spot/Fut</span></th>
              <th><span className="th-label">Funding</span></th>
              <th><span className="th-label">Faixa</span></th>
              <th><span className="th-label">Ordens</span></th>
              <th><span className="th-label">Tags</span></th>
              <th
                className={cn('sortable', sortConfig.key === 'status' && 'active-sort')}
                onClick={() => handleSort('status')}
              >
                <span className="th-label">Status</span>
                <span className="sort-arrow">{sortConfig.key === 'status' ? (sortConfig.dir === 'desc' ? '▼' : '▲') : '↕'}</span>
              </th>
              <th><span className="th-label">Ação</span></th>
            </tr>
          </thead>
          <tbody id="tableBody">
            {filteredOpps.map((opp) => (
              <tr key={opp.id} className={opp.status === 'KILLED' ? 'row-trap' : ''}>
                {/* Score */}
                <td>
                  <div className={getScoreClass(opp.score, opp.status)}>
                    {opp.score}
                  </div>
                </td>

                {/* Symbol */}
                <td style={{ textAlign: 'left !important' as any }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div className="coin-wrapper" style={{ borderColor: getCoinColor(opp.symbol) }}>
                      <span style={{ fontSize: 12, fontWeight: 'bold', color: getCoinColor(opp.symbol) }}>
                        {opp.symbol.slice(0, 1)}
                      </span>
                    </div>
                    <div>
                      <div style={{ fontFamily: 'monospace', color: '#fff', fontWeight: 700 }}>
                        {opp.symbol}
                      </div>
                      <div style={{ fontSize: 10, color: '#94A3B8' }}>
                        {opp.pair || 'USDT'}
                      </div>
                    </div>
                  </div>
                </td>

                {/* Spread */}
                <td>
                  <div className={cn('spread-val', opp.spread_net_pct >= 0 ? 'spread-positive' : 'spread-negative')}>
                    {opp.spread_net_pct >= 0 ? '+' : ''}{opp.spread_net_pct.toFixed(2)}%
                  </div>
                  {opp.spread_exec_pct !== opp.spread_net_pct && (
                    <span className="spread-sub">
                      Exec: {opp.spread_exec_pct.toFixed(2)}%
                    </span>
                  )}
                </td>

                {/* Volume */}
                <td style={{ fontFamily: 'monospace', color: '#888' }}>
                  {formatUSD(opp.volume_24h_usd)}
                </td>

                {/* Capacity */}
                <td className={getCapacityClass(opp.capacity_band)}>
                  <div className="cap-main">
                    {opp.capacity_pct?.toFixed(0) || 0}%
                  </div>
                  <div className="cap-sub">
                    {opp.capacity_band}
                  </div>
                  {opp.capacity_band === 'RED' && (
                    <div className="cap-limiters">
                      <span className="limiter-tag limiter-liquidity">LIQ</span>
                    </div>
                  )}
                </td>

                {/* Exchanges */}
                <td>
                  <div style={{ fontSize: 9, color: '#64748b', textTransform: 'uppercase', fontWeight: 700, marginBottom: 4 }}>
                    {opp.exchange_spot}
                  </div>
                  <div style={{ fontSize: 9, color: '#3b82f6', textTransform: 'uppercase', fontWeight: 700 }}>
                    {opp.exchange_futures}
                  </div>
                  {opp.is_cross_venue && (
                    <span style={{ fontSize: 7, color: '#f59e0b', textTransform: 'uppercase' }}>
                      Cross-venue
                    </span>
                  )}
                </td>

                {/* Price */}
                <td style={{ fontFamily: 'monospace', fontSize: 11 }}>
                  <div style={{ color: '#ddd' }}>
                    S: {opp.price_spot?.toFixed(6) || '0'}
                  </div>
                  <div style={{ color: '#ddd' }}>
                    F: {opp.price_futures?.toFixed(6) || '0'}
                  </div>
                </td>

                {/* Funding */}
                <td>
                  <div className="funding-val" style={{ color: opp.funding_rate >= 0 ? '#FBBF24' : '#60A5FA' }}>
                    {(opp.funding_rate * 100)?.toFixed(4)}%
                  </div>
                  <div className="funding-sub">
                    {(opp.funding_interval_hours || 8)}h
                  </div>
                </td>

                {/* Range */}
                <td style={{ fontFamily: 'monospace', fontSize: 10, color: '#888' }}>
                  - / -
                </td>

                {/* Orders */}
                <td style={{ fontFamily: 'monospace', fontSize: 11, color: '#888' }}>
                  {opp.orders_to_fill_spot || 1}/{opp.orders_to_fill_fut || 1}
                </td>

                {/* Tags */}
                <td>
                  {renderTags(opp.tags)}
                </td>

                {/* Status */}
                <td>
                  <span className={getStatusClass(opp.status)}>
                    {opp.status}
                  </span>
                </td>

                {/* Actions */}
                <td>
                  <div className="action-btns">
                    <button
                      className="action-btn action-btn-view"
                      onClick={() => handleViewDetails(opp)}
                      title="Ver detalhes"
                      aria-label={`Ver detalhes de ${opp.symbol}`}
                    >
                      <Eye size={14} />
                    </button>
                    {opp.status === 'READY' && (
                      <button
                        className="action-btn action-btn-exec"
                        onClick={() => handleExecute(opp)}
                        title="Executar"
                        aria-label={`Executar ${opp.symbol}`}
                      >
                        <PlayIcon size={14} />
                      </button>
                    )}
                    <button
                      className="action-btn action-btn-kill"
                      onClick={() => handleKill(opp)}
                      title="Descartar"
                      aria-label={`Descartar ${opp.symbol}`}
                    >
                      <X size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="sort-indicator" style={{ marginTop: 16 }}>
        <span style={{ color: '#94A3B8' }}>Cycle:</span>
        <span className="sort-indicator-key">#{meta?.cycle_id || 0}</span>
        <span style={{ margin: '0 16px', color: '#334155' }}>|</span>
        <span style={{ color: '#94A3B8' }}>Total:</span>
        <span className="summary-value">{filteredOpps.length}</span>
        <span style={{ margin: '0 8px', color: '#334155' }}>|</span>
        <span style={{ color: '#94A3B8' }}>Ativas:</span>
        <span className="summary-value" style={{ color: '#10B981' }}>{activeOpps}</span>
        <span style={{ margin: '0 8px', color: '#334155' }}>|</span>
        <span style={{ color: '#94A3B8' }}>Ready:</span>
        <span className="summary-value" style={{ color: '#3B82F6' }}>{readyOpps}</span>
      </div>

      {/* Connection Status */}
      <div style={{ height: 40, display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 11, marginTop: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div className={cn(
            'w-2 h-2 rounded-full',
            meta ? 'bg-green animate-pulse' : 'bg-red'
          )} style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: meta ? '#10B981' : '#EF4444' }} />
          <span style={{ color: meta ? '#10B981' : '#EF4444' }}>
            {meta ? 'Dados atualizados' : 'Aguardando dados...'}
          </span>
        </div>
        {error && (
          <div style={{ color: '#EF4444', display: 'flex', alignItems: 'center', gap: 6 }}>
            <AlertCircle size={14} />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* KPI Bar (optional, can be removed if not needed) */}
      {/* <KpiBar
        activeOpportunities={activeOpps}
        bestSpread={bestSpread}
        avgSpread={avgSpread}
        pipelineLatencyMs={meta?.pipeline_latency_ms || 0}
      /> */}
    </div>
  )
}
