/**
 * Card component
 * Seguindo FRONTEND-SPEC.md specification
 */

import { HTMLAttributes, forwardRef } from 'react'
import { cn } from '@/utils/formatters'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass'
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const baseStyles = 'rounded-xl border border-border overflow-hidden'

    const variants = {
      default: 'bg-card',
      glass: 'bg-card/70 backdrop-blur-xl'
    }

    return (
      <div
        className={cn(baseStyles, variants[variant], className)}
        ref={ref}
        {...props}
      />
    )
  }
)

Card.displayName = 'Card'

const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      className={cn('px-6 py-4 border-b border-border', className)}
      ref={ref}
      {...props}
    />
  )
)

CardHeader.displayName = 'CardHeader'

const CardTitle = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      className={cn('text-lg font-semibold text-white', className)}
      ref={ref}
      {...props}
    />
  )
)

CardTitle.displayName = 'CardTitle'

const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p
      className={cn('text-sm text-muted mt-1', className)}
      ref={ref}
      {...props}
    />
  )
)

CardDescription.displayName = 'CardDescription'

const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      className={cn('px-6 py-4', className)}
      ref={ref}
      {...props}
    />
  )
)

CardContent.displayName = 'CardContent'

const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      className={cn('px-6 py-4 border-t border-border bg-surface/50', className)}
      ref={ref}
      {...props}
    />
  )
)

CardFooter.displayName = 'CardFooter'

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
