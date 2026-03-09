/**
 * Select component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { SelectHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/utils/formatters'
import { ChevronDown } from 'lucide-react'

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: { value: string; label: string }[]
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, options, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-xs text-muted mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          <select
            className={cn(
              'w-full appearance-none bg-surface border border-border rounded-lg px-3 py-2 pr-10 text-white transition-colors focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold disabled:opacity-50 disabled:cursor-not-allowed',
              className
            )}
            ref={ref}
            {...props}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDown
            className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted pointer-events-none"
          />
        </div>
      </div>
    )
  }
)

Select.displayName = 'Select'

export { Select }
