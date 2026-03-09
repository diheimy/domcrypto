/**
 * KpiCard component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { cn } from '@/utils/formatters'
import type { ReactNode } from 'react'

interface KpiCardProps {
  title: string
  value: string | number
  change?: string
  trend?: 'up' | 'down' | 'neutral'
  icon: ReactNode
  className?: string
}

export function KpiCard({
  title,
  value,
  change,
  trend = 'neutral',
  icon,
  className
}: KpiCardProps) {
  const trendColors = {
    up: 'text-green',
    down: 'text-red',
    neutral: 'text-muted'
  }

  const trendIcons = {
    up: '↑',
    down: '↓',
    neutral: '→'
  }

  return (
    <div
      className={cn(
        'glass rounded-xl p-6 border border-border transition-all hover:border-gold/30',
        className
      )}
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-muted text-sm">{title}</span>
        <div className="text-gold">{icon}</div>
      </div>
      <div className="text-3xl font-bold font-mono text-white">
        {value}
      </div>
      {change && (
        <div className={cn('text-sm mt-2 flex items-center gap-1', trendColors[trend])}>
          <span>{trendIcons[trend]}</span>
          <span>{change}</span>
        </div>
      )}
    </div>
  )
}
