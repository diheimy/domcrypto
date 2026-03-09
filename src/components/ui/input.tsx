/**
 * Input component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { InputHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/utils/formatters'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, ...props }, ref) => {
    const baseStyles = 'w-full bg-surface border border-border rounded-lg px-3 py-2 text-white placeholder-muted transition-colors focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold disabled:opacity-50 disabled:cursor-not-allowed'

    return (
      <div className="w-full">
        {label && (
          <label className="block text-xs text-muted mb-2">
            {label}
          </label>
        )}
        <input
          className={cn(baseStyles, error && 'border-red focus:border-red focus:ring-red', className)}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="mt-1 text-xs text-red">{error}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export { Input }
