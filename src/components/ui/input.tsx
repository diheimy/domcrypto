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
    const baseStyles = 'w-full bg-surface border border-border rounded-md px-3 py-2 text-foreground placeholder:text-muted-foreground transition-colors focus:outline-none focus:border-ring focus:ring-1 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed font-sans'

    return (
      <div className="w-full">
        {label && (
          <label className="block text-xs text-muted-foreground mb-2 font-sans">
            {label}
          </label>
        )}
        <input
          className={cn(baseStyles, error && 'border-destructive focus:border-destructive focus:ring-destructive', className)}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="mt-1 text-xs text-destructive font-sans">{error}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export { Input }
