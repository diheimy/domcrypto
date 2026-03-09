'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, Activity, DollarSign, Clock, Server, Zap } from 'lucide-react'

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

interface KPIProps {
  title: string
  value: string | number
  change?: string
  icon: React.ReactNode
  trend?: 'up' | 'down' | 'neutral'
}

function KpiCard({ title, value, change, icon, trend = 'neutral' }: KPIProps) {
  return (
    <div className="glass rounded-xl p-6 border border-border hover:border-gold/50 transition-all duration-300 hover:shadow-glow">
      <div className="flex items-center justify-between mb-4">
        <span className="text-muted text-sm">{title}</span>
        <div className="text-gold">{icon}</div>
      </div>
      <div className="text-3xl font-bold font-mono text-white mb-2">{value}</div>
      {change && (
        <div className={`text-sm ${trend === 'up' ? 'text-green' : trend === 'down' ? 'text-red' : 'text-muted'}`}>
          {change}
        </div>
      )}
    </div>
  )
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-gold border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted">Carregando dados...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-muted">Visão geral do sistema de arbitragem</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <KpiCard
          title="Oportunidades Ativas"
          value={activeOpps}
          change={`${readyOpps} prontas para execução`}
          icon={<TrendingUp size={24} />}
          trend="up"
        />
        <KpiCard
          title="Melhor Spread"
          value={`+${bestSpread.toFixed(2)}%`}
          icon={<DollarSign size={24} />}
          trend="up"
        />
        <KpiCard
          title="Spread Médio"
          value={`+${avgSpread.toFixed(2)}%`}
          icon={<Activity size={24} />}
          trend={avgSpread > 0.5 ? 'up' : 'neutral'}
        />
        <KpiCard
          title="Volume 24h Total"
          value={`$${(totalVolume / 1000000).toFixed(2)}M`}
          icon={<Clock size={24} />}
          trend="neutral"
        />
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-6">
        <div className="glass rounded-xl p-6 border border-border">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Server size={20} className="text-gold" />
            Status do Sistema
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-muted">Backend Python</span>
              <span className="text-green font-mono">● Conectado</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted">Latência Pipeline</span>
              <span className="text-gold font-mono">{meta?.pipeline_latency_ms || 0}ms</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted">Cycle ID</span>
              <span className="text-muted font-mono">#{meta?.cycle_id || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted">Última Atualização</span>
              <span className="text-muted font-mono">
                {meta?.ts ? new Date(meta.ts).toLocaleTimeString() : '--:--:--'}
              </span>
            </div>
          </div>
        </div>

        <div className="glass rounded-xl p-6 border border-border">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Zap size={20} className="text-gold" />
            Contagem de Oportunidades
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-muted">Total</span>
              <span className="text-white font-mono">{meta?.counts?.total || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted">Ativas</span>
              <span className="text-green font-mono">{meta?.counts?.active || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted">Observação</span>
              <span className="text-yellow-500 font-mono">{meta?.counts?.obs || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted">Descartadas</span>
              <span className="text-red font-mono">{meta?.counts?.killed || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Opportunities Table */}
      <div className="glass rounded-xl border border-border overflow-hidden mt-6">
        <div className="p-4 border-b border-border">
          <h2 className="text-lg font-semibold text-white">Top Oportunidades</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-surface">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">Score</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">Símbolo</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">Exchanges</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">Spread</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {opportunities
                .sort((a, b) => b.spread_net_pct - a.spread_net_pct)
                .slice(0, 10)
                .map((opp) => (
                  <tr key={opp.id} className="hover:bg-hover transition-colors">
                    <td className="px-4 py-3 font-mono text-white">
                      <span className={`px-2 py-1 rounded text-xs ${
                        opp.score >= 70 ? 'bg-green/20 text-green' :
                        opp.score >= 50 ? 'bg-yellow-500/20 text-yellow-500' :
                        'bg-red/20 text-red'
                      }`}>
                        {opp.score}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-white">{opp.symbol}</td>
                    <td className="px-4 py-3 text-muted text-sm">
                      {opp.id.replace(`${opp.symbol}-`, '').replace('_', ' / ')}
                    </td>
                    <td className="px-4 py-3 font-mono text-green">+{opp.spread_net_pct.toFixed(2)}%</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        opp.status === 'ACTIVE' ? 'bg-green/20 text-green' :
                        opp.status === 'READY' ? 'bg-blue/20 text-blue' :
                        'bg-muted/20 text-muted'
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
