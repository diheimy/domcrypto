'use client'

import { useState } from 'react'
import { Save, RotateCcw } from 'lucide-react'
import { useSettings } from '@/hooks'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { SUPPORTED_SPOT_EXCHANGES, SUPPORTED_FUTURES_EXCHANGES } from '@/utils/constants'
import type { UserSettings } from '@/types'

export function SettingsForm() {
  const { settings, loading, error, updateSettings, refresh } = useSettings()

  const [localSettings, setLocalSettings] = useState<Partial<UserSettings> | null>(null)
  const [saving, setSaving] = useState(false)

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const currentSettings = localSettings || settings

  const handleChange = <K extends keyof UserSettings>(
    key: K,
    value: UserSettings[K]
  ) => {
    setLocalSettings((prev) => (prev ? { ...prev, [key]: value } : { [key]: value } as Partial<UserSettings>))
  }

  const handleSave = async () => {
    if (!localSettings) return
    setSaving(true)
    try {
      await updateSettings(localSettings)
      setLocalSettings(null)
    } catch (err) {
      console.error('Failed to save settings:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    setLocalSettings(null)
    refresh()
  }

  const hasChanges = localSettings !== null

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted">
          Ajuste os parâmetros de trading e preferências do sistema
        </p>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleReset} disabled={!hasChanges}>
            <RotateCcw size={16} />
            <span className="ml-2">Descartar</span>
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleSave}
            disabled={!hasChanges || saving}
          >
            <Save size={16} />
            <span className="ml-2">{saving ? 'Salvando...' : 'Salvar'}</span>
          </Button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="glass rounded-xl p-4 border border-red/50">
          <p className="text-red text-sm">{error}</p>
        </div>
      )}

      {/* Profile Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white text-lg">Perfil</CardTitle>
          <CardDescription>Configurações básicas do perfil de trading</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            label="Nome do Perfil"
            value={currentSettings?.profile_name || 'default'}
            onChange={(e) => handleChange('profile_name', e.target.value)}
            placeholder="default"
          />
        </CardContent>
      </Card>

      {/* Trading Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white text-lg">Trading</CardTitle>
          <CardDescription>Parâmetros de entrada e risco</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Min Spread */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-muted">Spread Mínimo (%)</label>
              <span className="text-gold font-mono text-sm">
                {(currentSettings?.min_spread_pct || 0.5).toFixed(2)}%
              </span>
            </div>
            <Slider
              min={0.1}
              max={5}
              step={0.1}
              value={currentSettings?.min_spread_pct || 0.5}
              onChange={(e) => handleChange('min_spread_pct', Number(e.target.value))}
              valueLabel={`${(currentSettings?.min_spread_pct || 0.5).toFixed(2)}%`}
            />
          </div>

          {/* Min Score */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-muted">Score Mínimo</label>
              <span className="text-gold font-mono text-sm">
                {currentSettings?.min_score || 50}
              </span>
            </div>
            <Slider
              min={0}
              max={100}
              step={5}
              value={currentSettings?.min_score || 50}
              onChange={(e) => handleChange('min_score', Number(e.target.value))}
              valueLabel={String(currentSettings?.min_score || 50)}
            />
          </div>

          {/* Min Volume */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-muted">Volume Mínimo 24h (USD)</label>
              <span className="text-gold font-mono text-sm">
                ${(currentSettings?.min_volume_usd || 100000).toLocaleString()}
              </span>
            </div>
            <Slider
              min={0}
              max={1000000}
              step={50000}
              value={currentSettings?.min_volume_usd || 100000}
              onChange={(e) => handleChange('min_volume_usd', Number(e.target.value))}
              valueLabel={`$${((currentSettings?.min_volume_usd || 100000) / 1000000).toFixed(2)}M`}
            />
          </div>

          {/* Min Persistence */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-muted">Persistência Mínima (min)</label>
              <span className="text-gold font-mono text-sm">
                {currentSettings?.min_persistence_min || 0}min
              </span>
            </div>
            <Slider
              min={0}
              max={60}
              step={5}
              value={currentSettings?.min_persistence_min || 0}
              onChange={(e) => handleChange('min_persistence_min', Number(e.target.value))}
              valueLabel={`${currentSettings?.min_persistence_min || 0}min`}
            />
          </div>
        </CardContent>
      </Card>

      {/* Capital Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white text-lg">Capital</CardTitle>
          <CardDescription>Gerenciamento de bankroll e posição</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            label="Bankroll Total (USD)"
            type="number"
            value={currentSettings?.bankroll_usd || 10000}
            onChange={(e) => handleChange('bankroll_usd', Number(e.target.value))}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Entrada Mínima (USD)"
              type="number"
              value={currentSettings?.entry_min_usd || 100}
              onChange={(e) => handleChange('entry_min_usd', Number(e.target.value))}
            />
            <Input
              label="Entrada Máxima (USD)"
              type="number"
              value={currentSettings?.entry_max_usd || 1000}
              onChange={(e) => handleChange('entry_max_usd', Number(e.target.value))}
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm text-muted">Hedge (%)</label>
              <span className="text-gold font-mono text-sm">
                {currentSettings?.hedge_pct || 100}%
              </span>
            </div>
            <Slider
              min={0}
              max={100}
              step={10}
              value={currentSettings?.hedge_pct || 100}
              onChange={(e) => handleChange('hedge_pct', Number(e.target.value))}
              valueLabel={`${currentSettings?.hedge_pct || 100}%`}
            />
          </div>
        </CardContent>
      </Card>

      {/* Exchange Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white text-lg">Exchanges</CardTitle>
          <CardDescription>Selecione as exchanges ativas para spot e futuros</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Spot Exchanges */}
          <div>
            <label className="text-sm text-muted mb-3 block">Exchanges Spot</label>
            <div className="grid grid-cols-2 gap-3">
              {([...SUPPORTED_SPOT_EXCHANGES] as string[]).map((exchange) => {
                const isActive = currentSettings?.spots?.includes(exchange) || false
                return (
                  <button
                    key={exchange}
                    onClick={() => {
                      const spots = isActive
                        ? currentSettings?.spots?.filter((s) => s !== exchange) || []
                        : [...(currentSettings?.spots || []), exchange]
                      handleChange('spots', spots)
                    }}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      isActive
                        ? 'bg-gold/10 border-gold text-white'
                        : 'bg-surface border-border text-muted hover:border-gold/50'
                    }`}
                  >
                    <div className="font-medium capitalize">{exchange}</div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Futures Exchanges */}
          <div>
            <label className="text-sm text-muted mb-3 block">Exchanges Futuros</label>
            <div className="grid grid-cols-2 gap-3">
              {([...SUPPORTED_FUTURES_EXCHANGES] as string[]).map((exchange) => {
                const isActive = currentSettings?.futures?.includes(exchange) || false
                return (
                  <button
                    key={exchange}
                    onClick={() => {
                      const futures = isActive
                        ? currentSettings?.futures?.filter((f) => f !== exchange) || []
                        : [...(currentSettings?.futures || []), exchange]
                      handleChange('futures', futures)
                    }}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      isActive
                        ? 'bg-gold/10 border-gold text-white'
                        : 'bg-surface border-border text-muted hover:border-gold/50'
                    }`}
                  >
                    <div className="font-medium capitalize">{exchange}</div>
                  </button>
                )
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Advanced Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white text-lg">Avançado</CardTitle>
          <CardDescription>Preferências adicionais</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-white">Cross-venue</div>
              <div className="text-xs text-muted">
                Permitir arbitragem entre exchanges diferentes
              </div>
            </div>
            <Switch
              checked={currentSettings?.allow_cross ?? true}
              onChange={(e) => handleChange('allow_cross', e.target.checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-white">Mesma Exchange</div>
              <div className="text-xs text-muted">
                Permitir arbitragem na mesma exchange
              </div>
            </div>
            <Switch
              checked={currentSettings?.allow_same ?? true}
              onChange={(e) => handleChange('allow_same', e.target.checked)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-white">Esconder Bloqueadas</div>
              <div className="text-xs text-muted">
                Ocultar oportunidades com moedas bloqueadas
              </div>
            </div>
            <Switch
              checked={currentSettings?.hide_blocked ?? false}
              onChange={(e) => handleChange('hide_blocked', e.target.checked)}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
