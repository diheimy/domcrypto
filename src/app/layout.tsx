import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'DomCrypto - Bot de Arbitragem',
  description: 'Sistema de arbitragem de criptomoedas Spot/Futuros',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>
        <div className="min-h-screen bg-background">
          {children}
        </div>
      </body>
    </html>
  )
}
