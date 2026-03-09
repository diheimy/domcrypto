export const runtime = 'edge'

export async function GET() {
  return Response.json({
    status: 'healthy',
    service: 'domcrypto-frontend',
    version: '0.2.0',
    timestamp: Date.now()
  })
}
