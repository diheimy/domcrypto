/**
 * SpreadCell component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { formatPercent } from '@/utils/formatters'
import { cn } from '@/utils/formatters'

interface SpreadCellProps {
  spread_net_pct: number
  spread_exec_pct?: number
  showGross?: boolean
}

export function SpreadCell({ spread_net_pct, spread_exec_pct, showGross = false }: SpreadCellProps) {
  const isPositive = spread_net_pct > 0
  const isNegative = spread_net_pct < 0

  return (
    <div className="flex flex-col">
      <span
        className={cn(
          'font-mono font-bold',
          isPositive ? 'text-green' : isNegative ? 'text-red' : 'text-muted'
        )}
      >
        {formatPercent(spread_net_pct)}
      </span>
      {showGross && spread_exec_pct !== undefined && (
        <span className="text-xs text-muted font-mono">
          Gross: {formatPercent(spread_exec_pct)}
        </span>
      )}
    </div>
  )
}
