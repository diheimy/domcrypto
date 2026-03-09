import { NextRequest } from 'next/server'

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      try {
        // Send mock data for now
        const mockData = {
          items: [
            {
              id: 'BTC-binance-binance_futures',
              symbol: 'BTC',
              pair: 'BTC/USDT',
              exchange_spot: 'binance',
              exchange_futures: 'binance_futures',
              is_cross_venue: false,
              price_spot: 67500,
              price_futures: 67650,
              spread_exec_pct: 0.22,
              spread_net_pct: 0.02,
              roi_net_pct: 0.01,
              profit_usd: 1.50,
              capacity_pct: 85,
              capacity_band: 'GREEN' as const,
              entry_leg_usd: 100,
              spot_top_book_usd: 50000,
              futures_top_book_usd: 75000,
              volume_24h_usd: 2500000,
              funding_rate: 0.0001,
              funding_interval_hours: 8,
              next_funding_at: Math.floor(Date.now() / 1000) + 28800,
              orders_to_fill_spot: 1,
              orders_to_fill_fut: 1,
              fill_status: 'OK',
              spot_px_start: 67500,
              spot_px_limit: 67480,
              fut_px_start: 67650,
              fut_px_limit: 67670,
              score: 75,
              trust_score: 80,
              quality_level: 'HIGH',
              status: 'ACTIVE' as const,
              execution_decision: 'EXECUTE',
              kill_reason: null,
              persistence_minutes: 5,
              tags: ['high-liquidity'],
              ts_created: Math.floor(Date.now() / 1000) - 300,
              ts_updated: Math.floor(Date.now() / 1000)
            }
          ],
          meta: {
            cycle_id: 1,
            ts: Date.now(),
            counts: {
              total: 1,
              active: 1,
              obs: 0,
              killed: 0
            },
            pipeline_latency_ms: 150
          }
        }

        // Send initial data
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(mockData)}\n\n`))

        // Keep connection alive with periodic updates
        const interval = setInterval(() => {
          const updatedData = {
            ...mockData,
            meta: {
              ...mockData.meta,
              ts: Date.now()
            }
          }
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(updatedData)}\n\n`))
        }, 3000)

        // Cleanup on close
        request.signal.addEventListener('abort', () => {
          clearInterval(interval)
          controller.close()
        })
      } catch (error) {
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
