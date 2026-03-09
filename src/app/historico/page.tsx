'use client'

import { useState } from 'react'
import { History, RefreshCw } from 'lucide-react'
import { usePnLHistory } from '@/hooks'
import { PnlSummary } from '@/components/historico/PnlSummary'
import { PnlTable } from '@/components/historico/PnlTable'
import { PipelineSnapshots } from '@/components/historico/PipelineSnapshots'
import { Button } from '@/components/ui/button'

export default function HistoricoPage() {
  const [days, setDays] = useState(30)
  const { items, total, loading, error, refresh } = usePnLHistory(days)

  const handleRefresh = () => {
    refresh()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted font-body">Carregando histórico...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display text-white mb-2">Histórico</h1>
          <p className="text-muted font-body">Registro de operações e pipeline snapshots</p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="bg-surface border border-border rounded-lg px-4 py-2 text-white text-sm focus:outline-none focus:border-primary font-body"
          >
            <option value={7}>Últimos 7 dias</option>
            <option value={15}>Últimos 15 dias</option>
            <option value={30}>Últimos 30 dias</option>
            <option value={90}>Últimos 90 dias</option>
          </select>

          <Button variant="outline" size="sm" onClick={handleRefresh}>
            <RefreshCw size={18} />
            <span className="hidden sm:inline ml-2 font-body">Atualizar</span>
          </Button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="glass rounded-xl p-4 border border-red/50">
          <p className="text-red text-sm">{error}</p>
        </div>
      )}

      {/* PnL Summary */}
      <PnlSummary items={items} />

      {/* PnL Table */}
      <div className="glass rounded-xl border border-border overflow-hidden">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-lg font-semibold font-display text-white flex items-center gap-2">
            <History size={20} className="text-primary" />
            Operações
          </h2>
          <span className="text-sm text-muted font-body">{total} operações</span>
        </div>
        <PnlTable items={items} />
      </div>

      {/* Pipeline Snapshots */}
      <PipelineSnapshots items={[]} />
    </div>
  )
}
