/**
 * CapacityBadge component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { cn } from '@/utils/formatters'
import type { CapacityBand } from '@/types'
import { BarChart3, BarChart2, BarChart } from 'lucide-react'

interface CapacityBadgeProps {
  band: CapacityBand
  capacity_pct?: number
  showLabel?: boolean
}

export function CapacityBadge({ band, capacity_pct, showLabel = true }: CapacityBadgeProps) {
  const colors = {
    GREEN: 'text-green bg-green/20',
    YELLOW: 'text-primary bg-primary/20',
    RED: 'text-red bg-red/20'
  }

  const icons = {
    GREEN: BarChart3,
    YELLOW: BarChart2,
    RED: BarChart
  }

  const labels = {
    GREEN: 'HIGH',
    YELLOW: 'MED',
    RED: 'LOW'
  }

  const Icon = icons[band]
  const colorClass = colors[band]

  return (
    <div className="inline-flex flex-col items-center gap-1">
      <span
        className={cn(
          'inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors font-body',
          colorClass
        )}
      >
        <Icon size={12} />
        {showLabel && labels[band]}
      </span>
      {capacity_pct !== undefined && (
        <span className="text-xs font-mono text-muted">
          {capacity_pct.toFixed(1)}%
        </span>
      )}
    </div>
  )
}
