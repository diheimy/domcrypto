/**
 * ExchangeCell component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { getExchangeDisplayName, isFuturesExchange, cn } from '@/utils/formatters'
import { ArrowRight } from 'lucide-react'

interface ExchangeCellProps {
  exchange_spot: string
  exchange_futures: string
  is_cross_venue: boolean
  showArrow?: boolean
}

export function ExchangeCell({
  exchange_spot,
  exchange_futures,
  is_cross_venue,
  showArrow = true
}: ExchangeCellProps) {
  const spotName = getExchangeDisplayName(exchange_spot)
  const futuresName = getExchangeDisplayName(exchange_futures)
  const isSpotFutures = isFuturesExchange(exchange_futures)

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <span className="text-sm text-white font-medium">{spotName}</span>
        {showArrow && (
          <ArrowRight size={12} className="text-muted" />
        )}
        <span className="text-sm text-white font-medium">{futuresName}</span>
      </div>
      <div className="flex items-center gap-2 text-xs">
        <span className="text-muted">Spot</span>
        <span className="text-muted">→</span>
        <span className={cn(
          'text-muted',
          isSpotFutures && 'text-gold'
        )}>
          {isSpotFutures ? 'Futures' : 'Spot'}
        </span>
      </div>
      {is_cross_venue && (
        <span className="text-xs text-gold/80 mt-0.5">
          Cross-venue
        </span>
      )}
    </div>
  )
}
