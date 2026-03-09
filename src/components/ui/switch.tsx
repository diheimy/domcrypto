/**
 * Switch component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { InputHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/utils/formatters'

export interface SwitchProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
}

const Switch = forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, label, ...props }, ref) => {
    // className is intentionally ignored - Switch has its own styling
    void className
    return (
      <label className="flex items-center cursor-pointer">
        <div className="relative">
          <input
            type="checkbox"
            className="sr-only"
            ref={ref}
            {...props}
          />
          <div
            className={cn(
              'w-10 h-6 rounded-full transition-colors',
              props.checked ? 'bg-gold' : 'bg-surface border border-border'
            )}
          >
            <div
              className={cn(
                'absolute top-1 w-4 h-4 rounded-full bg-white transition-transform',
                props.checked ? 'left-5' : 'left-1'
              )}
            />
          </div>
        </div>
        {label && (
          <span className="ml-3 text-sm text-muted">{label}</span>
        )}
      </label>
    )
  }
)

Switch.displayName = 'Switch'

export { Switch }
