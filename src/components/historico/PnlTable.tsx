'use client'

import type { PnLRecord } from '@/types'
import { formatCurrency, formatPercent } from '@/utils/formatters'

interface PnlTableProps {
  items: PnLRecord[]
}

export function PnlTable({ items }: PnlTableProps) {
  if (items.length === 0) {
    return (
      <div className="p-8 text-center text-muted">
        Nenhuma operação registrada no período
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-surface border-b border-border">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Símbolo
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Exchanges
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Entrada
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Saída
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Spread Entrada
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Spread Saída
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Capital
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              PnL
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              PnL %
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
              Status
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {items.map((record) => (
            <tr key={record.id} className="hover:bg-hover transition-colors">
              <td className="px-4 py-3 font-mono text-white font-medium">
                {record.symbol}
              </td>
              <td className="px-4 py-3 text-sm text-muted">
                <div>{record.exchange_spot}</div>
                <div className="text-xs">→ {record.exchange_futures}</div>
              </td>
              <td className="px-4 py-3 text-sm text-muted">
                {new Date(record.entry_at).toLocaleDateString('pt-BR', {
                  day: '2-digit',
                  month: '2-digit',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </td>
              <td className="px-4 py-3 text-sm text-muted">
                {record.exit_at
                  ? new Date(record.exit_at).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit'
                    })
                  : '—'}
              </td>
              <td className="px-4 py-3 font-mono text-sm">
                <span className={record.entry_spread >= 0.5 ? 'text-green' : 'text-muted'}>
                  {record.entry_spread.toFixed(2)}%
                </span>
              </td>
              <td className="px-4 py-3 font-mono text-sm">
                {record.exit_spread !== null ? (
                  <span className={record.exit_spread >= 0 ? 'text-green' : 'text-red'}>
                    {record.exit_spread.toFixed(2)}%
                  </span>
                ) : (
                  '—'
                )}
              </td>
              <td className="px-4 py-3 font-mono text-white">
                {formatCurrency(record.capital_usd)}
              </td>
              <td className="px-4 py-3 font-mono">
                {record.pnl_usd !== null ? (
                  <span className={record.pnl_usd >= 0 ? 'text-green' : 'text-red'}>
                    {formatCurrency(record.pnl_usd)}
                  </span>
                ) : (
                  '—'
                )}
              </td>
              <td className="px-4 py-3 font-mono">
                {record.pnl_pct !== null ? (
                  <span className={record.pnl_pct >= 0 ? 'text-green' : 'text-red'}>
                    {formatPercent(record.pnl_pct / 100)}
                  </span>
                ) : (
                  '—'
                )}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    record.status === 'CLOSED'
                      ? 'bg-green/20 text-green'
                      : 'bg-blue/20 text-blue'
                  }`}
                >
                  {record.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
