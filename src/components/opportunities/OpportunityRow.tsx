/**
 * OpportunityRow component
 * Seguindo FRONTEND-SPEC.md specification
 */

import type { OpportunityItemV2 } from '@/types'
import { ScoreBadge } from './ScoreBadge'
import { StatusBadge } from './StatusBadge'
import { CapacityBadge } from './CapacityBadge'
import { SpreadCell } from './SpreadCell'
import { FundingCell } from './FundingCell'
import { ExchangeCell } from './ExchangeCell'
import { ActionButtons } from './ActionButtons'
import { formatUSD, formatPercent } from '@/utils/formatters'
import { cn } from '@/utils/formatters'

interface OpportunityRowProps {
  opp: OpportunityItemV2
  onView?: (opp: OpportunityItemV2) => void
  onExecute?: (opp: OpportunityItemV2) => void
  onKill?: (opp: OpportunityItemV2) => void
  highlightNew?: boolean
}

export function OpportunityRow({
  opp,
  onView,
  onExecute,
  onKill,
  highlightNew = false
}: OpportunityRowProps) {
  return (
    <tr
      className={cn(
        'hover:bg-hover transition-colors',
        highlightNew && 'bg-gold/5 animate-pulse'
      )}
    >
      {/* Score */}
      <td className="px-4 py-3">
        <ScoreBadge score={opp.score} showQuality={false} />
      </td>

      {/* Symbol */}
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gold/20 flex items-center justify-center text-gold text-xs font-bold">
            {opp.symbol.slice(0, 1)}
          </div>
          <div>
            <div className="font-mono text-white">{opp.symbol}</div>
            <div className="text-xs text-muted">{opp.pair}</div>
          </div>
        </div>
      </td>

      {/* Spread */}
      <td className="px-4 py-3">
        <SpreadCell spread_net_pct={opp.spread_net_pct} showGross />
      </td>

      {/* ROI */}
      <td className="px-4 py-3">
        <div>
          <div className={cn(
            'font-mono font-bold',
            opp.roi_net_pct >= 0 ? 'text-gold' : 'text-red'
          )}>
            {formatPercent(opp.roi_net_pct)}
          </div>
          <div className="text-xs text-muted">
            {formatUSD(opp.profit_usd)}
          </div>
        </div>
      </td>

      {/* Capacity */}
      <td className="px-4 py-3">
        <CapacityBadge band={opp.capacity_band} capacity_pct={opp.capacity_pct} />
      </td>

      {/* Exchanges */}
      <td className="px-4 py-3">
        <ExchangeCell
          exchange_spot={opp.exchange_spot}
          exchange_futures={opp.exchange_futures}
          is_cross_venue={opp.is_cross_venue}
        />
      </td>

      {/* Volume */}
      <td className="px-4 py-3 font-mono text-muted">
        {formatUSD(opp.volume_24h_usd)}
      </td>

      {/* Funding */}
      <td className="px-4 py-3">
        <FundingCell
          funding_rate={opp.funding_rate}
          funding_interval_hours={opp.funding_interval_hours}
          next_funding_at={opp.next_funding_at}
        />
      </td>

      {/* Status */}
      <td className="px-4 py-3">
        <StatusBadge status={opp.status} />
      </td>

      {/* Actions */}
      <td className="px-4 py-3">
        <ActionButtons
          status={opp.status}
          onView={() => onView?.(opp)}
          onExecute={() => onExecute?.(opp)}
          onKill={() => onKill?.(opp)}
        />
      </td>
    </tr>
  )
}
