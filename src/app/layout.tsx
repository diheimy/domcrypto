import Sidebar from '@/components/layout/Sidebar'
import type { Metadata } from 'next'

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
          <Sidebar />
          <main className="lg:pl-[256px] min-h-screen">
            <div className="p-4 lg:p-6">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  )
}
