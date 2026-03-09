/**
 * FilterDrawer component
 * Seguindo FRONTEND-SPEC.md specification
 */

'use client'

import { X, SlidersHorizontal, RotateCcw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/utils/formatters'

interface FilterDrawerProps {
  isOpen: boolean
  onClose: () => void
  onReset: () => void
  children: React.ReactNode
}

export function FilterDrawer({
  isOpen,
  onClose,
  onReset,
  children
}: FilterDrawerProps) {
  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          onClick={onClose}
        />
      )}

      {/* Drawer */}
      <div
        className={cn(
          'fixed top-0 right-0 h-full w-80 bg-card border-l border-border z-50 transform transition-transform duration-300 ease-in-out',
          isOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <SlidersHorizontal size={20} className="text-gold" />
            <h2 className="text-lg font-semibold text-white">Filtros</h2>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={onReset}
              className="text-muted hover:text-white"
              title="Resetar filtros"
            >
              <RotateCcw size={16} />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="text-muted hover:text-white"
            >
              <X size={20} />
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 overflow-y-auto h-[calc(100%-80px)]">
          {children}
        </div>
      </div>
    </>
  )
}
