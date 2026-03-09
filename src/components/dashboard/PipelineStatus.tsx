/**
 * PipelineStatus component
 * Seguindo FRONTEND-SPEC.md specification
 */

'use client'

import { cn } from '@/utils/formatters'
import { Activity, CheckCircle, AlertCircle, Pause } from 'lucide-react'

interface PipelineStatusProps {
  isRunning: boolean
  cycleId: number
  latencyMs: number
  lastUpdate?: number
}

export function PipelineStatus({
  isRunning,
  cycleId,
  latencyMs,
  lastUpdate
}: PipelineStatusProps) {
  const getStatusColor = () => {
    if (!isRunning) return 'bg-yellow-500'
    if (latencyMs > 500) return 'bg-yellow-500'
    return 'bg-green'
  }

  const getStatusIcon = () => {
    if (!isRunning) return <Pause size={20} className="text-yellow-500" />
    if (latencyMs > 500) return <AlertCircle size={20} className="text-yellow-500" />
    return <CheckCircle size={20} className="text-green" />
  }

  const getStatusText = () => {
    if (!isRunning) return 'Pausado'
    if (latencyMs > 500) return 'Lento'
    return 'Executando'
  }

  const formatLastUpdate = (ts?: number) => {
    if (!ts) return 'Nunca'
    const diff = Date.now() - ts
    const seconds = Math.floor(diff / 1000)
    if (seconds < 60) return `${seconds}s atrás`
    const minutes = Math.floor(seconds / 60)
    return `${minutes}min atrás`
  }

  return (
    <div className="glass rounded-xl p-4 border border-border">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Activity size={20} className="text-gold" />
          Status do Pipeline
        </h3>
        {getStatusIcon()}
      </div>

      <div className="space-y-3">
        {/* Status */}
        <div className="flex items-center justify-between">
          <span className="text-muted text-sm">Status</span>
          <span className={cn(
            'text-sm font-medium',
            isRunning ? 'text-green' : 'text-yellow-500'
          )}>
            {getStatusText()}
          </span>
        </div>

        {/* Cycle */}
        <div className="flex items-center justify-between">
          <span className="text-muted text-sm">Cycle ID</span>
          <span className="text-white font-mono">#{cycleId}</span>
        </div>

        {/* Latency */}
        <div className="flex items-center justify-between">
          <span className="text-muted text-sm">Latência</span>
          <span className={cn(
            'text-white font-mono',
            latencyMs > 500 ? 'text-yellow-500' : 'text-green'
          )}>
            {latencyMs}ms
          </span>
        </div>

        {/* Last Update */}
        <div className="flex items-center justify-between">
          <span className="text-muted text-sm">Última Atualização</span>
          <span className="text-muted text-sm font-mono">
            {formatLastUpdate(lastUpdate)}
          </span>
        </div>

        {/* Connection indicator */}
        <div className="flex items-center gap-2 pt-3 border-t border-border">
          <div className={cn(
            'w-2 h-2 rounded-full animate-pulse',
            getStatusColor()
          )} />
          <span className="text-xs text-muted">
            {isRunning ? 'Conectado ao backend' : 'Desconectado'}
          </span>
        </div>
      </div>
    </div>
  )
}
