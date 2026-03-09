/**
 * SearchFilter component
 * Seguindo FRONTEND-SPEC.md specification
 */

'use client'

import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'

interface SearchFilterProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  label?: string
}

export function SearchFilter({
  value,
  onChange,
  placeholder = 'Buscar moeda...',
  label = 'Buscar'
}: SearchFilterProps) {
  return (
    <div className="w-full">
      <label className="block text-xs text-muted mb-2">
        {label}
      </label>
      <div className="relative">
        <Input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="pl-10"
        />
        <Search
          size={18}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted"
        />
      </div>
    </div>
  )
}
