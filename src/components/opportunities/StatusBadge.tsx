/**
 * StatusBadge component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { cn, getStatusColor, getStatusLabel } from '@/utils/formatters'
import type { OpStatus } from '@/types'
import { Activity, CheckCircle, Eye, XCircle, AlertCircle } from 'lucide-react'

interface StatusBadgeProps {
  status: OpStatus
  showLabel?: boolean
}

export function StatusBadge({ status, showLabel = true }: StatusBadgeProps) {
  const colorClass = getStatusColor(status)
  const label = getStatusLabel(status)

  const icons = {
    ACTIVE: Activity,
    READY: CheckCircle,
    OBSERVATION_ONLY: Eye,
    KILLED: XCircle,
    DEGRADED: AlertCircle
  }

  const Icon = icons[status] || Activity

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium transition-colors',
        colorClass
      )}
    >
      <Icon size={12} />
      {showLabel && label}
    </span>
  )
}
