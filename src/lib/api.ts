/**
 * API Client para DomCrypto Frontend
 * Seguindo FRONTEND-SPEC.md specification
 */

import type {
  UserSettings,
  UpdateSettingsRequest,
  OpportunitiesResponse,
  PnLHistoryResponse,
  PipelineSnapshotsResponse,
  HealthResponse
} from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''

// =============================================================================
// HEALTH CHECK
// =============================================================================

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) throw new Error('Failed to fetch health')
  return res.json()
}

// =============================================================================
// OPPORTUNITIES
// =============================================================================

export async function fetchOpportunities(params?: {
  status?: string
  min_score?: number
  min_spread?: number
  limit?: number
}): Promise<OpportunitiesResponse> {
  const searchParams = new URLSearchParams()
  if (params?.status) searchParams.set('status', params.status)
  if (params?.min_score) searchParams.set('min_score', params.min_score.toString())
  if (params?.min_spread) searchParams.set('min_spread', params.min_spread.toString())
  if (params?.limit) searchParams.set('limit', params.limit.toString())

  const res = await fetch(`${API_BASE}/api/v1/opportunities?${searchParams}`)
  if (!res.ok) throw new Error('Failed to fetch opportunities')
  return res.json()
}

export async function fetchOpportunityDetail(id: string): Promise<{ item: unknown; exists: boolean }> {
  const res = await fetch(`${API_BASE}/api/v1/opportunities/${id}`)
  if (!res.ok) throw new Error('Failed to fetch opportunity detail')
  return res.json()
}

// =============================================================================
// SETTINGS
// =============================================================================

export async function fetchSettings(): Promise<UserSettings> {
  const res = await fetch(`${API_BASE}/api/v1/settings`)
  if (!res.ok) throw new Error('Failed to fetch settings')
  return res.json()
}

export async function updateSettings(
  settings: UpdateSettingsRequest
): Promise<UserSettings> {
  const res = await fetch(`${API_BASE}/api/v1/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings)
  })
  if (!res.ok) throw new Error('Failed to update settings')
  return res.json()
}

// =============================================================================
// PnL HISTORY
// =============================================================================

export async function fetchPnLHistory(params?: {
  days?: number
  status?: string
}): Promise<PnLHistoryResponse> {
  const searchParams = new URLSearchParams()
  if (params?.days) searchParams.set('days', params.days.toString())
  if (params?.status) searchParams.set('status', params.status)

  const res = await fetch(`${API_BASE}/api/v1/pnl?${searchParams}`)
  if (!res.ok) throw new Error('Failed to fetch PnL history')
  return res.json()
}

// =============================================================================
// PIPELINE SNAPSHOTS
// =============================================================================

export async function fetchPipelineSnapshots(params?: {
  limit?: number
}): Promise<PipelineSnapshotsResponse> {
  const searchParams = new URLSearchParams()
  if (params?.limit) searchParams.set('limit', params.limit.toString())

  const res = await fetch(`${API_BASE}/api/v1/snapshots?${searchParams}`)
  if (!res.ok) throw new Error('Failed to fetch pipeline snapshots')
  return res.json()
}

// =============================================================================
// SSE CONNECTION
// =============================================================================

export interface SSECallbacks {
  onData: (data: unknown) => void
  onError?: (error: Event) => void
  onOpen?: () => void
}

export function connectToOpportunitiesSSE({
  onData,
  onError,
  onOpen
}: SSECallbacks): () => void {
  const eventSource = new EventSource(`${API_BASE}/api/sse/opportunities`)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onData(data)
    } catch (error) {
      console.error('Failed to parse SSE data:', error)
    }
  }

  eventSource.onopen = () => {
    onOpen?.()
  }

  eventSource.onerror = (error) => {
    console.error('SSE Error:', error)
    onError?.(error)
    eventSource.close()
  }

  return () => {
    eventSource.close()
  }
}

// =============================================================================
// WEBSOCKET CONNECTION
// =============================================================================

export interface WebSocketCallbacks {
  onMessage: (data: unknown) => void
  onError?: (error: Event) => void
  onOpen?: () => void
  onClose?: () => void
}

export function connectToOpportunitiesWS({
  onMessage,
  onError,
  onOpen,
  onClose
}: WebSocketCallbacks): () => void {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || `ws://${window.location.host}/ws/opportunities`
  const socket = new WebSocket(wsUrl)

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (error) {
      console.error('Failed to parse WebSocket data:', error)
    }
  }

  socket.onopen = () => {
    onOpen?.()
  }

  socket.onerror = (error) => {
    console.error('WebSocket Error:', error)
    onError?.(error)
  }

  socket.onclose = () => {
    onClose?.()
  }

  return () => {
    socket.close()
  }
}
