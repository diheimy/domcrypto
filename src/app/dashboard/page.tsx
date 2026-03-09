'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, Activity, DollarSign, Clock, Server, Zap, RefreshCw } from 'lucide-react'
import { KpiCard } from '@/components/dashboard/KpiCard'

interface Opportunity {
  id: string
  symbol: string
  spread_net_pct: number
  score: number
  status: string
  volume_24h_usd: number
}

interface Meta {
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

function formatUSD(value: number) {
  if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`
  if (value >= 1000) return `$${(value / 1000).toFixed(2)}K`
  return `$${value.toFixed(2)}`
}

function formatPercent(value: number) {
  return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`
}

export default function DashboardPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [meta, setMeta] = useState<Meta | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/sse/opportunities')
        const data = await res.json()
        setOpportunities(data.items || [])
        setMeta(data.meta || null)
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Calculate KPIs
  const activeOpps = opportunities.filter(o => o.status === 'ACTIVE').length
  const readyOpps = opportunities.filter(o => o.status === 'READY').length
  const bestSpread = opportunities.length > 0
    ? Math.max(...opportunities.map(o => o.spread_net_pct))
    : 0
  const avgSpread = opportunities.length > 0
    ? opportunities.reduce((acc, o) => acc + o.spread_net_pct, 0) / opportunities.length
    : 0
  const totalVolume = opportunities.reduce((acc, o) => acc + o.volume_24h_usd, 0)

  const refreshData = async () => {
    try {
      const res = await fetch('/api/sse/opportunities')
      const data = await res.json()
      setOpportunities(data.items || [])
      setMeta(data.meta || null)
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 border-3 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">Visão geral do sistema de arbitragem</p>
        </div>
        <button
          onClick={refreshData}
          className="p-2 rounded-md bg-secondary hover:bg-surface-hover text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Atualizar dados"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          title="Oportunidades Ativas"
          value={activeOpps}
          change={`${readyOpps} prontas`}
          icon={<TrendingUp size={20} />}
          trend="up"
        />
        <KpiCard
          title="Melhor Spread"
          value={formatPercent(bestSpread)}
          icon={<DollarSign size={20} />}
          trend="up"
        />
        <KpiCard
          title="Spread Médio"
          value={formatPercent(avgSpread)}
          icon={<Activity size={20} />}
          trend={avgSpread > 0.5 ? 'up' : 'neutral'}
        />
        <KpiCard
          title="Volume 24h"
          value={formatUSD(totalVolume)}
          icon={<Clock size={20} />}
          trend="neutral"
        />
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="glass rounded-md p-5 border border-border">
          <h2 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
            <Server size={16} className="text-primary" />
            Status do Sistema
          </h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Backend Python</span>
              <span className="text-green font-mono">● Online</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Latência Pipeline</span>
              <span className="text-primary font-mono">{meta?.pipeline_latency_ms || 0}ms</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Cycle ID</span>
              <span className="font-mono text-muted-foreground">#{meta?.cycle_id || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Última Atualização</span>
              <span className="font-mono text-muted-foreground">
                {meta?.ts ? new Date(meta.ts).toLocaleTimeString() : '--:--:--'}
              </span>
            </div>
          </div>
        </div>

        <div className="glass rounded-md p-5 border border-border">
          <h2 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
            <Zap size={16} className="text-primary" />
            Contagem
          </h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Total</span>
              <span className="text-foreground font-mono">{meta?.counts?.total || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Ativas</span>
              <span className="text-green font-mono">{meta?.counts?.active || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Observação</span>
              <span className="text-yellow font-mono">{meta?.counts?.obs || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Descartadas</span>
              <span className="text-red font-mono">{meta?.counts?.killed || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Opportunities Table */}
      <div className="glass rounded-md border border-border overflow-hidden">
        <div className="px-5 py-4 border-b border-border">
          <h2 className="text-sm font-semibold text-foreground">Top 10 Oportunidades</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface">
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Score</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Símbolo</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Exchanges</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Spread</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {opportunities
                .sort((a, b) => b.spread_net_pct - a.spread_net_pct)
                .slice(0, 10)
                .map((opp) => (
                  <tr key={opp.id} className="hover:bg-surface-hover transition-colors">
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-mono font-medium ${
                        opp.score >= 70 ? 'bg-green/15 text-green' :
                        opp.score >= 50 ? 'bg-yellow/15 text-yellow' :
                        'bg-red/15 text-red'
                      }`}>
                        {opp.score}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono font-medium text-foreground">{opp.symbol}</td>
                    <td className="px-4 py-3 text-muted-foreground text-xs">
                      {opp.id.replace(`${opp.symbol}-`, '').replace('_', ' / ')}
                    </td>
                    <td className="px-4 py-3 font-mono text-green">{formatPercent(opp.spread_net_pct)}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        opp.status === 'ACTIVE' ? 'bg-green/15 text-green' :
                        opp.status === 'READY' ? 'bg-blue/15 text-blue' :
                        'bg-muted/15 text-muted-foreground'
                      }`}>
                        {opp.status}
                      </span>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
