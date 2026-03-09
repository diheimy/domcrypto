/**
 * FundingCell component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { formatFundingRate, formatTime, cn } from '@/utils/formatters'

interface FundingCellProps {
  funding_rate: number
  funding_interval_hours?: number
  next_funding_at?: number | null
}

export function FundingCell({
  funding_rate,
  funding_interval_hours,
  next_funding_at
}: FundingCellProps) {
  const isPositive = funding_rate > 0
  const nextFunding = next_funding_at ? formatTime(next_funding_at) : null

  return (
    <div className="flex flex-col gap-0.5">
      <span
        className={cn(
          'font-mono text-sm',
          isPositive ? 'text-green' : 'text-red'
        )}
      >
        {formatFundingRate(funding_rate)}
      </span>
      {nextFunding && (
        <span className="text-xs text-muted">
          {nextFunding}
        </span>
      )}
      {funding_interval_hours && (
        <span className="text-xs text-muted">
          {funding_interval_hours}h interval
        </span>
      )}
    </div>
  )
}
