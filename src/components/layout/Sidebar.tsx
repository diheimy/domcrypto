'use client'

import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import {
  LayoutDashboard,
  ArrowLeftRight,
  History,
  Settings,
  Activity,
  ChevronLeft,
  ChevronRight,
  Menu,
  X
} from 'lucide-react'
import { cn } from '@/utils/formatters'

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Spot × Futuros', href: '/spot-futuros', icon: ArrowLeftRight },
  { name: 'Histórico', href: '/historico', icon: History },
  { name: 'Configurações', href: '/configuracoes', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [systemStatus, setSystemStatus] = useState<'online' | 'offline'>('offline')

  // Check system status
  useEffect(() => {
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
        onClick={() => setMobileOpen(!mobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-surface hover:bg-surface-hover border border-border transition-colors"
        aria-label={mobileOpen ? 'Fechar menu' : 'Abrir menu'}
      >
        {mobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Mobile Overlay */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/80 z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 h-full flex flex-col border-r border-sidebar-border bg-sidebar transition-all duration-300 z-40 lg:translate-x-0",
          collapsed ? "w-[68px]" : "w-[240px]",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Logo */}
        <div className={cn(
          "flex items-center border-b border-sidebar-border h-16 px-4",
          collapsed ? "justify-center px-0" : "justify-start gap-3"
        )}>
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
            <Activity className="w-4 h-4 text-primary-foreground" />
          </div>
          {!collapsed && (
            <span className="font-bold text-lg text-foreground tracking-tight">
              Dom<span className="text-primary">Crypto</span>
            </span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group",
                  collapsed ? "justify-center" : "",
                  isActive
                    ? "bg-primary/10 text-primary shadow-glow"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-foreground"
                )}
              >
                <item.icon className={cn("w-5 h-5 flex-shrink-0", isActive && "text-primary")} />
                {!collapsed && (
                  <span className="text-sm font-medium">{item.name}</span>
                )}
              </Link>
            )
          })}
        </nav>

        {/* System Status */}
        <div className={cn("border-t border-sidebar-border p-4", collapsed ? "px-2" : "")}>
          <div className={cn(
            "flex items-center gap-2 text-sm",
            collapsed ? "justify-center" : ""
          )}>
            <div className={cn(
              "w-2 h-2 rounded-full",
              systemStatus === 'online' ? 'bg-green animate-pulse-slow' : 'bg-red'
            )} />
            {!collapsed && (
              <>
                <span className={systemStatus === 'online' ? 'text-green' : 'text-red'}>
                  {systemStatus === 'online' ? 'Online' : 'Offline'}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="hidden lg:flex items-center justify-center h-12 border-t border-sidebar-border text-muted-foreground hover:text-foreground transition-colors"
          aria-label={collapsed ? 'Expandir sidebar' : 'Recolher sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </aside>
    </>
  )
}
