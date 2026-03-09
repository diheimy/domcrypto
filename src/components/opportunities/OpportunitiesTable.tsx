/**
 * OpportunitiesTable component
 * Seguindo FRONTEND-SPEC.md specification
 */

'use client'

import type { OpportunityItemV2 } from '@/types'
import { OpportunityRow } from './OpportunityRow'
import { AlertCircle } from 'lucide-react'

interface OpportunitiesTableProps {
  data: OpportunityItemV2[]
  onExecute?: (opp: OpportunityItemV2) => void
  onViewDetails?: (opp: OpportunityItemV2) => void
  onKill?: (opp: OpportunityItemV2) => void
  sortBy?: 'score' | 'spread' | 'roi' | 'capacity'
  sortOrder?: 'asc' | 'desc'
}

export function OpportunitiesTable({
  data,
  onExecute,
  onViewDetails,
  onKill,
  sortBy = 'spread',
  sortOrder = 'desc'
}: OpportunitiesTableProps) {
  const sortedData = [...data].sort((a, b) => {
    let comparison = 0

    switch (sortBy) {
      case 'score':
        comparison = b.score - a.score
        break
      case 'spread':
        comparison = b.spread_net_pct - a.spread_net_pct
        break
      case 'roi':
        comparison = b.roi_net_pct - a.roi_net_pct
        break
      case 'capacity':
        comparison = b.capacity_pct - a.capacity_pct
        break
      default:
        comparison = 0
    }

    return sortOrder === 'desc' ? comparison : -comparison
  })

  if (data.length === 0) {
    return (
      <div className="p-12 text-center">
        <AlertCircle size={48} className="mx-auto text-muted mb-4" />
        <p className="text-muted">Nenhuma oportunidade encontrada</p>
        <p className="text-sm text-muted mt-2">
          Ajuste os filtros ou aguarde novas oportunidades
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-surface border-b border-border">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Score
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Ativo
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Spread
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              ROI
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Capacidade
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Exchanges
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Volume 24h
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Funding
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Status
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Ações
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {sortedData.map((opp) => (
            <OpportunityRow
              key={opp.id}
              opp={opp}
              onView={onViewDetails}
              onExecute={onExecute}
              onKill={onKill}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
}
