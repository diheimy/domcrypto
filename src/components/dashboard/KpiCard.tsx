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
    neutral: 'text-muted-foreground'
  }

  const trendIcons = {
    up: '↑',
    down: '↓',
    neutral: '→'
  }

  return (
    <div
      className={cn(
        'glass rounded-md p-5 border border-border transition-all duration-300 hover:border-primary/30 hover:shadow-glow',
        className
      )}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-muted-foreground text-sm font-sans">{title}</span>
        <div className="text-primary">{icon}</div>
      </div>
      <div className="text-2xl font-bold font-mono text-foreground mb-1">
        {value}
      </div>
      {change && (
        <div className={cn('text-xs flex items-center gap-1 font-sans', trendColors[trend])}>
          <span>{trendIcons[trend]}</span>
          <span>{change}</span>
        </div>
      )}
    </div>
  )
}
