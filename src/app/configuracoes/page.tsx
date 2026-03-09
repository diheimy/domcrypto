'use client'

import { Settings as SettingsIcon } from 'lucide-react'
import { SettingsForm } from '@/components/configuracoes/SettingsForm'

export default function ConfiguracoesPage() {
  return (
    <div className="max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold font-display text-white mb-2 flex items-center gap-3">
          <SettingsIcon size={32} className="text-primary" />
          Configurações
        </h1>
        <p className="text-muted font-body">Ajuste os parâmetros do sistema de trading</p>
      </div>

      {/* Settings Form */}
      <SettingsForm />
    </div>
  )
}
