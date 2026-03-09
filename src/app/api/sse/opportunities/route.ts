import { NextRequest } from 'next/server'

export const dynamic = 'force-dynamic'

// Backend API URL - usa variável de ambiente ou default para produção
const BACKEND_URL = process.env.BACKEND_API_URL || 'http://python-backend:8000'

export async function GET(request: NextRequest) {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      try {
        // Fetch initial data from backend
        const fetchFromBackend = async () => {
          try {
            const res = await fetch(`${BACKEND_URL}/api/v1/opportunities`, {
              signal: request.signal,
            })
            if (res.ok) {
              const data = await res.json()
              return data
            }
          } catch (error) {
            console.error('Error fetching from backend:', error)
          }
          return null
        }

        // Send initial data
        let data = await fetchFromBackend()
        if (data) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`))
        } else {
          // Send empty payload if backend is unavailable
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ items: [], meta: { cycle_id: 0, ts: Date.now(), counts: { total: 0, active: 0, obs: 0, killed: 0 }, pipeline_latency_ms: 0 } })}\n\n`))
        }

        // Keep connection alive with periodic updates from backend
        const interval = setInterval(async () => {
          try {
            const freshData = await fetchFromBackend()
            if (freshData) {
              controller.enqueue(encoder.encode(`data: ${JSON.stringify(freshData)}\n\n`))
            } else {
              // Send heartbeat with timestamp update
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ items: [], meta: { cycle_id: 0, ts: Date.now(), counts: { total: 0, active: 0, obs: 0, killed: 0 }, pipeline_latency_ms: 0, status: 'DEGRADED' } })}\n\n`))
            }
          } catch (error) {
            console.error('Error in SSE interval:', error)
          }
        }, 3000)

        // Cleanup on close
        request.signal.addEventListener('abort', () => {
          clearInterval(interval)
          controller.close()
        })
      } catch (error) {
        console.error('SSE stream error:', error)
        controller.error(error)
      }
    }
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no'
    }
  })
}
