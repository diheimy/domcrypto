/**
 * ScoreBadge component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { cn, getScoreColor, getScoreBg, getScoreQuality } from '@/utils/formatters'

interface ScoreBadgeProps {
  score: number
  size?: 'sm' | 'md' | 'lg'
  showQuality?: boolean
}

export function ScoreBadge({ score, size = 'md', showQuality = false }: ScoreBadgeProps) {
  const colorClass = getScoreColor(score)
  const bgClass = getScoreBg(score)
  const quality = getScoreQuality(score)

  const sizes = {
    sm: 'text-xs px-1.5 py-0.5',
    md: 'text-sm px-2 py-1',
    lg: 'text-base px-3 py-1.5'
  }

  return (
    <div className="inline-flex flex-col items-center">
      <span
        className={cn(
          'font-mono font-bold rounded transition-colors',
          bgClass,
          colorClass,
          sizes[size]
        )}
      >
        {score}
      </span>
      {showQuality && (
        <span className="text-xs text-muted mt-0.5">{quality}</span>
      )}
    </div>
  )
}
