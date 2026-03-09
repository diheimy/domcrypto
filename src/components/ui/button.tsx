/**
 * Button component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/utils/formatters'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  asChild?: boolean
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-lg font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none'

    const variants = {
      primary: 'bg-gold text-black hover:bg-gold/90 focus:ring-gold shadow-lg shadow-gold/20',
      secondary: 'bg-transparent border border-gold text-gold hover:bg-gold/10 focus:ring-gold',
      ghost: 'bg-transparent hover:bg-hover text-muted hover:text-white focus:ring-muted',
      danger: 'bg-red/20 text-red hover:bg-red/30 focus:ring-red',
      outline: 'bg-transparent border border-border text-white hover:border-gold focus:ring-gold'
    }

    const sizes = {
      sm: 'h-8 px-3 text-xs',
      md: 'h-10 px-4 text-sm',
      lg: 'h-12 px-6 text-base'
    }

    return (
      <button
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        ref={ref}
        {...props}
      />
    )
  }
)

Button.displayName = 'Button'

export { Button }
