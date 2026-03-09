'use client'

import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react'
import type { PnLRecord } from '@/types'
import { formatCurrency } from '@/utils/formatters'

interface PnlSummaryProps {
  items: PnLRecord[]
}

export function PnlSummary({ items }: PnlSummaryProps) {
  // Calculate metrics
  const closedTrades = items.filter((t) => t.status === 'CLOSED')
  const openTrades = items.filter((t) => t.status === 'OPEN')

  const totalPnl = closedTrades.reduce((acc, t) => acc + (t.pnl_usd || 0), 0)
  const winningTrades = closedTrades.filter((t) => (t.pnl_usd || 0) > 0)
  const losingTrades = closedTrades.filter((t) => (t.pnl_usd || 0) <= 0)

  const winRate =
    closedTrades.length > 0 ? (winningTrades.length / closedTrades.length) * 100 : 0

  const avgWin =
    winningTrades.length > 0
      ? winningTrades.reduce((acc, t) => acc + (t.pnl_usd || 0), 0) / winningTrades.length
      : 0

  const avgLoss =
    losingTrades.length > 0
      ? losingTrades.reduce((acc, t) => acc + (t.pnl_usd || 0), 0) / losingTrades.length
      : 0

  const profitFactor =
    avgLoss !== 0 ? Math.abs(avgWin / avgLoss) : avgWin > 0 ? Infinity : 0

  const totalCapital = items.reduce((acc, t) => acc + t.capital_usd, 0)

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Total PnL */}
      <div className="glass rounded-xl p-6 border border-border hover:border-gold/50 transition-all duration-300">
        <div className="flex items-center justify-between mb-4">
          <span className="text-muted text-sm">PnL Total</span>
          <div className={totalPnl >= 0 ? 'text-green' : 'text-red'}>
            {totalPnl >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
          </div>
        </div>
        <div
          className={`text-3xl font-bold font-mono ${
            totalPnl >= 0 ? 'text-green' : 'text-red'
          }`}
        >
          {formatCurrency(totalPnl)}
        </div>
        <div className="text-sm text-muted mt-2">
          {closedTrades.length} operações fechadas
        </div>
      </div>

      {/* Win Rate */}
      <div className="glass rounded-xl p-6 border border-border hover:border-gold/50 transition-all duration-300">
        <div className="flex items-center justify-between mb-4">
          <span className="text-muted text-sm">Taxa de Acerto</span>
          <div className="text-gold">
            <Activity size={20} />
          </div>
        </div>
        <div className="text-3xl font-bold font-mono text-white">{winRate.toFixed(1)}%</div>
        <div className="text-sm text-muted mt-2">
          {winningTrades.length} vitórias / {losingTrades.length} derrotas
        </div>
      </div>

      {/* Profit Factor */}
      <div className="glass rounded-xl p-6 border border-border hover:border-gold/50 transition-all duration-300">
        <div className="flex items-center justify-between mb-4">
          <span className="text-muted text-sm">Profit Factor</span>
          <div className="text-gold">
            <DollarSign size={20} />
          </div>
        </div>
        <div className="text-3xl font-bold font-mono text-white">
          {profitFactor === Infinity ? '∞' : profitFactor.toFixed(2)}
        </div>
        <div className="text-sm text-muted mt-2">
          Ganho médio: {formatCurrency(Math.max(0, avgWin))}
        </div>
      </div>

      {/* Capital Employed */}
      <div className="glass rounded-xl p-6 border border-border hover:border-gold/50 transition-all duration-300">
        <div className="flex items-center justify-between mb-4">
          <span className="text-muted text-sm">Capital Empregado</span>
          <div className="text-blue">
            <TrendingUp size={20} />
          </div>
        </div>
        <div className="text-3xl font-bold font-mono text-white">
          {formatCurrency(totalCapital)}
        </div>
        <div className="text-sm text-muted mt-2">
          {openTrades.length} operações em aberto
        </div>
      </div>
    </div>
  )
}
