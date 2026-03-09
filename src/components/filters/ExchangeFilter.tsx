/**
 * ExchangeFilter component
 * Seguindo FRONTEND-SPEC.md specification
 */

'use client'

import { cn } from '@/utils/formatters'
import { EXCHANGE_LABELS } from '@/utils/constants'

interface ExchangeFilterProps {
  title: string
  exchanges: string[]
  activeExchanges: string[]
  onToggle: (exchange: string) => void
}

export function ExchangeFilter({
  title,
  exchanges,
  activeExchanges,
  onToggle
}: ExchangeFilterProps) {
  const isActive = (exchange: string) => activeExchanges.includes(exchange)

  return (
    <div className="w-full">
      <h4 className="text-xs text-muted uppercase tracking-wider mb-3 pb-2 border-b border-border">
        {title}
      </h4>
      <div className="flex flex-wrap gap-2">
        {exchanges.map((exchange) => {
          const active = isActive(exchange)
          const label = EXCHANGE_LABELS[exchange] || exchange

          return (
            <button
              key={exchange}
              onClick={() => onToggle(exchange)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-xs font-medium transition-all border',
                active
                  ? 'bg-gold/20 border-gold text-gold'
                  : 'bg-surface border-border text-muted hover:border-gold/50'
              )}
            >
              {label}
            </button>
          )
        })}
      </div>
    </div>
  )
}
