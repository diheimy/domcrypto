/**
 * Slider component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { InputHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/utils/formatters'

export interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
  valueLabel?: string
}

const Slider = forwardRef<HTMLInputElement, SliderProps>(
  ({ className, label, valueLabel, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <div className="flex justify-between items-center mb-2">
            <label className="text-xs text-muted">{label}</label>
            {valueLabel && (
              <span className="text-xs font-mono text-gold">{valueLabel}</span>
            )}
          </div>
        )}
        <input
          type="range"
          className={cn(
            'w-full h-2 bg-surface rounded-lg appearance-none cursor-pointer accent-gold',
            'focus:outline-none focus:ring-2 focus:ring-gold/50',
            className
          )}
          ref={ref}
          {...props}
        />
      </div>
    )
  }
)

Slider.displayName = 'Slider'

export { Slider }
