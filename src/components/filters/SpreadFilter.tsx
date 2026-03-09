/**
 * SpreadFilter component
 * Seguindo FRONTEND-SPEC.md specification
 */

'use client'

import { Slider } from '@/components/ui/slider'
import { formatPercent } from '@/utils/formatters'

interface SpreadFilterProps {
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
  label?: string
}

export function SpreadFilter({
  value,
  onChange,
  min = 0,
  max = 5,
  step = 0.1,
  label = 'Spread Mínimo'
}: SpreadFilterProps) {
  return (
    <div className="w-full">
      <Slider
        label={label}
        valueLabel={formatPercent(value)}
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <div className="flex justify-between mt-1">
        <span className="text-xs text-muted">{formatPercent(min)}</span>
        <span className="text-xs text-muted">{formatPercent(max)}</span>
      </div>
    </div>
  )
}
