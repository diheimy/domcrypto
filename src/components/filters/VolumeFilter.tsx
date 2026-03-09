/**
 * VolumeFilter component
 * Seguindo FRONTEND-SPEC.md specification
 */

'use client'

import { Slider } from '@/components/ui/slider'
import { formatUSD } from '@/utils/formatters'

interface VolumeFilterProps {
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
  label?: string
}

export function VolumeFilter({
  value,
  onChange,
  min = 0,
  max = 1000000,
  step = 10000,
  label = 'Volume Mínimo 24h'
}: VolumeFilterProps) {
  return (
    <div className="w-full">
      <Slider
        label={label}
        valueLabel={formatUSD(value)}
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      <div className="flex justify-between mt-1">
        <span className="text-xs text-muted">{formatUSD(min)}</span>
        <span className="text-xs text-muted">{formatUSD(max)}</span>
      </div>
    </div>
  )
}
