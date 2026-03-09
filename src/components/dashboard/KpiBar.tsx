/**
 * KpiBar component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { KpiCard } from './KpiCard'
import { TrendingUp, DollarSign, Activity, Zap } from 'lucide-react'

interface KpiBarProps {
  activeOpportunities: number
  bestSpread: number
  avgSpread: number
  pipelineLatencyMs: number
}

export function KpiBar({
  activeOpportunities,
  bestSpread,
  avgSpread,
  pipelineLatencyMs
}: KpiBarProps) {
  const cards = [
    {
      title: 'Oportunidades Ativas',
      value: activeOpportunities,
      icon: <Activity size={20} />,
      trend: 'neutral' as const
    },
    {
      title: 'Melhor Spread',
      value: `+${bestSpread.toFixed(2)}%`,
      icon: <TrendingUp size={20} />,
      trend: 'up' as const,
      change: bestSpread > 0 ? 'Positivo' : undefined
    },
    {
      title: 'Spread Médio',
      value: `+${avgSpread.toFixed(2)}%`,
      icon: <DollarSign size={20} />,
      trend: avgSpread > 0 ? 'up' as const : 'down' as const
    },
    {
      title: 'Latência Pipeline',
      value: `${pipelineLatencyMs}ms`,
      icon: <Zap size={20} />,
      trend: 'neutral' as const
    }
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      {cards.map((card) => (
        <KpiCard key={card.title} {...card} />
      ))}
    </div>
  )
}
