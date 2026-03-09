'use client'

import { useState } from 'react'
import { Server, Clock, TrendingUp, Activity } from 'lucide-react'
import type { PipelineSnapshot } from '@/types'

interface PipelineSnapshotsProps {
  items: PipelineSnapshot[]
}

export function PipelineSnapshots({ items }: PipelineSnapshotsProps) {
  const [selectedSnapshot, setSelectedSnapshot] = useState<PipelineSnapshot | null>(null)

  if (items.length === 0) {
    return (
      <div className="glass rounded-xl p-6 border border-border">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Server size={20} className="text-gold" />
          Snapshots do Pipeline
        </h3>
        <p className="text-muted text-center py-8">
          Nenhum snapshot disponível
        </p>
      </div>
    )
  }

  return (
    <div className="glass rounded-xl p-6 border border-border">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Server size={20} className="text-gold" />
        Snapshots do Pipeline
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Snapshots List */}
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {items.slice(0, 20).map((snapshot) => (
            <button
              key={snapshot.id}
              onClick={() => setSelectedSnapshot(snapshot)}
              className={`w-full p-4 rounded-lg border text-left transition-all ${
                selectedSnapshot?.id === snapshot.id
                  ? 'bg-gold/10 border-gold'
                  : 'bg-surface border-border hover:border-gold/50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white font-mono font-medium">
                    Cycle #{snapshot.cycle_id}
                  </div>
                  <div className="text-xs text-muted mt-1 flex items-center gap-2">
                    <Clock size={12} />
                    {new Date(snapshot.ts).toLocaleString('pt-BR')}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-green font-mono text-sm">
                    {snapshot.count_active} ativas
                  </div>
                  <div className="text-xs text-muted">
                    {snapshot.count_raw} total
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Snapshot Details */}
        <div className="bg-surface rounded-lg p-4 border border-border">
          {selectedSnapshot ? (
            <div>
              <h4 className="text-white font-semibold mb-4">
                Cycle #{selectedSnapshot.cycle_id}
              </h4>

              <div className="space-y-4">
                <div>
                  <div className="text-xs text-muted mb-1">Timestamp</div>
                  <div className="text-white font-mono">
                    {new Date(selectedSnapshot.ts).toLocaleString('pt-BR')}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-muted mb-1">Total</div>
                    <div className="text-white font-mono text-lg">
                      {selectedSnapshot.count_raw}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted mb-1">Ativas</div>
                    <div className="text-green font-mono text-lg">
                      {selectedSnapshot.count_active}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted mb-1">Observação</div>
                    <div className="text-yellow-500 font-mono text-lg">
                      {selectedSnapshot.count_obs}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-muted mb-1">Descartadas</div>
                    <div className="text-red font-mono text-lg">
                      {selectedSnapshot.count_killed}
                    </div>
                  </div>
                </div>

                {selectedSnapshot.top_symbol && (
                  <div>
                    <div className="text-xs text-muted mb-1 flex items-center gap-1">
                      <TrendingUp size={12} />
                      Melhor Spread
                    </div>
                    <div className="text-green font-mono">
                      {selectedSnapshot.top_symbol}
                    </div>
                  </div>
                )}

                {selectedSnapshot.top_spread && (
                  <div>
                    <div className="text-xs text-muted mb-1 flex items-center gap-1">
                      <Activity size={12} />
                      Spread
                    </div>
                    <div className="text-green font-mono">
                      +{selectedSnapshot.top_spread.toFixed(2)}%
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-muted">
              Selecione um snapshot para ver detalhes
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
