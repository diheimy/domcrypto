'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  TrendingUp,
  History,
  Settings,
  Menu,
  X
} from 'lucide-react'

interface NavItem {
  name: string
  href: string
  icon: React.ReactNode
}

const navItems: NavItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: <LayoutDashboard size={20} /> },
  { name: 'Spot x Futuros', href: '/spot-futuros', icon: <TrendingUp size={20} /> },
  { name: 'Histórico', href: '/historico', icon: <History size={20} /> },
  { name: 'Configurações', href: '/configuracoes', icon: <Settings size={20} /> },
]

export default function Sidebar() {
  const pathname = usePathname()
  const [isOpen, setIsOpen] = useState(false)
  const [systemStatus, setSystemStatus] = useState<'online' | 'offline'>('offline')

  useEffect(() => {
    // Check system status
    const checkStatus = async () => {
      try {
        const res = await fetch('/health')
        if (res.ok) {
          setSystemStatus('online')
        }
      } catch {
        setSystemStatus('offline')
      }
    }
    checkStatus()
    const interval = setInterval(checkStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-card border border-border hover:border-gold transition-colors"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Overlay */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/80 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full w-64 bg-surface border-r border-border-gold transition-transform duration-300 z-40 lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-border">
          <h1 className="text-2xl font-bold text-gradient-gold">DomCrypto</h1>
          <p className="text-xs text-muted mt-1">Arbitragem Bot v0.2</p>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-gold-glow border-l-[3px] border-gold text-gold'
                    : 'hover:bg-hover border-l-[3px] border-transparent text-muted hover:text-white'
                }`}
              >
                {item.icon}
                <span className="font-medium">{item.name}</span>
              </Link>
            )
          })}
        </nav>

        {/* System Status */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${
              systemStatus === 'online' ? 'bg-green animate-pulse' : 'bg-red'
            }`} />
            <span className={systemStatus === 'online' ? 'text-green' : 'text-red'}>
              {systemStatus === 'online' ? '● Online' : '● Offline'}
            </span>
          </div>
        </div>
      </aside>
    </>
  )
}
