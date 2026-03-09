/**
 * SSE Connection utilities
 * Seguindo FRONTEND-SPEC.md specification
 */

import type { SSEPayload } from '@/types'

export interface SSEOptions {
  autoReconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export interface SSECallbacks {
  onData: (data: SSEPayload) => void
  onError?: (error: Event) => void
  onOpen?: () => void
  onClose?: () => void
}

/**
 * Connect to opportunities SSE endpoint
 * Returns unsubscribe function
 */
export function connectToOpportunities(
  callbacks: SSECallbacks,
  options: SSEOptions = {}
): () => void {
  const {
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5
  } = options

  let reconnectAttempts = 0
  let eventSource: EventSource | null = null
  let closed = false

  const connect = () => {
    if (closed) return

    eventSource = new EventSource('/api/sse/opportunities')

    eventSource.onmessage = (event) => {
      try {
        const data: SSEPayload = JSON.parse(event.data)
        callbacks.onData(data)
        reconnectAttempts = 0 // Reset on successful message
      } catch (error) {
        console.error('Failed to parse SSE data:', error)
      }
    }

    eventSource.onopen = () => {
      // SSE connection opened
      callbacks.onOpen?.()
      reconnectAttempts = 0
    }

    eventSource.onerror = (error) => {
      callbacks.onError?.(error)

      if (autoReconnect && reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++
        eventSource?.close()
        setTimeout(connect, reconnectInterval)
      } else {
        closed = true
        callbacks.onClose?.()
      }
    }
  }

  connect()

  return () => {
    closed = true
    eventSource?.close()
  }
}

/**
 * Simple SSE connection without auto-reconnect
 */
export function createSSEConnection(
  url: string,
  onMessage: (data: unknown) => void,
  onError?: (error: Event) => void
): () => void {
  const eventSource = new EventSource(url)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (error) {
      console.error('Failed to parse SSE message:', error)
    }
  }

  eventSource.onerror = (error) => {
    console.error('SSE connection error:', error)
    onError?.(error)
    eventSource.close()
  }

  return () => {
    eventSource.close()
  }
}
