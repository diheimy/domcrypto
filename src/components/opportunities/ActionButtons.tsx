/**
 * ActionButtons component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { Eye, Play, Square, MoreVertical } from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { OpStatus } from '@/types'

interface ActionButtonsProps {
  status: OpStatus
  onView?: () => void
  onExecute?: () => void
  onKill?: () => void
  disabled?: boolean
}

export function ActionButtons({
  status,
  onView,
  onExecute,
  onKill,
  disabled = false
}: ActionButtonsProps) {
  const canExecute = status === 'READY' || status === 'ACTIVE'
  const canKill = status !== 'KILLED'

  return (
    <div className="flex items-center gap-1">
      <Button
        variant="ghost"
        size="sm"
        onClick={onView}
        disabled={disabled}
        title="Ver detalhes"
      >
        <Eye size={16} />
      </Button>

      {canExecute && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onExecute}
          disabled={disabled}
          className="text-green hover:bg-green/20"
          title="Executar"
        >
          <Play size={16} />
        </Button>
      )}

      {canKill && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onKill}
          disabled={disabled}
          className="text-red hover:bg-red/20"
          title="Descartar"
        >
          <Square size={16} />
        </Button>
      )}

      <Button
        variant="ghost"
        size="sm"
        disabled={disabled}
        className="text-muted hover:text-white"
        title="Mais ações"
      >
        <MoreVertical size={16} />
      </Button>
    </div>
  )
}
