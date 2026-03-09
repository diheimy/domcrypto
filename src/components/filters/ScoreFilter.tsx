/**
 * ScoreFilter component
 * Seguindo FRONTEND-SPEC.md specification
 */

'use client'

import { Slider } from '@/components/ui/slider'

interface ScoreFilterProps {
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
  label?: string
}

export function ScoreFilter({
  value,
  onChange,
  min = 0,
  max = 100,
  step = 5,
  label = 'Score Mínimo'
}: ScoreFilterProps) {
  return (
    <div className="w-full">
      <Slider
        label={label}
        valueLabel={String(value)}
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <div className="flex justify-between mt-1 text-xs text-muted">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  )
}
