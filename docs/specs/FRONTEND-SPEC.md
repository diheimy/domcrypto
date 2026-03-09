# Frontend Next.js - Especificação de Desenvolvimento

**DomCrypto Frontend** - Dashboard de Arbitragem de Criptomoedas
Versão: 0.2.0 | Data: 2026-03-08

---

## 📋 Visão Geral

Frontend Next.js 14 com App Router para visualização em tempo real de oportunidades de arbitragem.

### Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| Framework | Next.js 14.2.5 (App Router) |
| Language | TypeScript 5.3+ |
| Styling | Tailwind CSS 3.4 |
| UI Components | Radix UI + ShadCN |
| Icons | Lucide React |
| State | Zustand |
| Charts | Recharts |
| Real-time | SSE (Server-Sent Events) |

---

## 📁 Estrutura de Pastas

```
src/
├── app/                              # Next.js App Router
│   ├── layout.tsx                    # Root layout
│   ├── page.tsx                      # Home page
│   ├── globals.css                   # Global styles
│   ├── dashboard/
│   │   ├── layout.tsx                # Dashboard layout com Sidebar
│   │   └── page.tsx                  # Dashboard com KPIs
│   ├── spot-futuros/
│   │   ├── layout.tsx                # Spot-Futuros layout
│   │   └── page.tsx                  # Tabela de oportunidades
│   ├── historico/
│   │   ├── layout.tsx
│   │   └── page.tsx                  # Histórico de trades
│   ├── configuracoes/
│   │   ├── layout.tsx
│   │   └── page.tsx                  # Configurações
│   ├── api/
│   │   └── sse/
│   │       └── opportunities/
│   │           └── route.ts          # SSE endpoint
│   └── health/
│       └── route.ts                  # Health check
├── components/
│   ├── layout/
│   │   └── Sidebar.tsx               # Sidebar de navegação
│   ├── dashboard/
│   │   ├── KpiCard.tsx               # Card de KPI
│   │   ├── KpiBar.tsx                # Barra de KPIs
│   │   └── PipelineStatus.tsx        # Status do pipeline
│   ├── opportunities/
│   │   ├── OpportunitiesTable.tsx    # Tabela principal
│   │   ├── OpportunityRow.tsx        # Linha da tabela
│   │   ├── ScoreBadge.tsx            # Badge de score
│   │   ├── SpreadCell.tsx            # Célula de spread
│   │   ├── CapacityBadge.tsx         # Badge de capacidade
│   │   ├── StatusBadge.tsx           # Badge de status
│   │   ├── ExchangeCell.tsx          # Célula de exchange
│   │   ├── FundingCell.tsx           # Célula de funding
│   │   └── ActionButtons.tsx         # Botões de ação
│   ├── filters/
│   │   ├── FilterDrawer.tsx          # Drawer de filtros
│   │   ├── ExchangeFilter.tsx        # Filtro de exchanges
│   │   ├── SpreadFilter.tsx          # Filtro de spread
│   │   └── ScoreFilter.tsx           # Filtro de score
│   └── ui/                           # Componentes base (ShadCN)
│       ├── button.tsx
│       ├── input.tsx
│       ├── select.tsx
│       ├── switch.tsx
│       ├── slider.tsx
│       └── card.tsx
├── hooks/
│   ├── useOpportunities.ts           # Hook de oportunidades
│   ├── useFilters.ts                 # Hook de filtros
│   └── useSettings.ts                # Hook de configurações
├── lib/
│   ├── api.ts                        # API client
│   ├── sse.ts                        # SSE connection
│   └── utils.ts                      # Utility functions
├── store/
│   └── opportunities.store.ts        # Zustand store
├── types/
│   ├── opportunity.ts                # Types de oportunidades
│   ├── settings.ts                   # Types de configurações
│   └── api.ts                        # Types de API
└── utils/
    ├── formatters.ts                 # Formatadores
    └── constants.ts                  # Constantes
```

---

## 🎨 Design System

### Cores

```typescript
// Tema Dark/Gold
const colors = {
  // Backgrounds
  background: '#000000',
  surface: '#060607',
  card: '#0f1319',
  hover: '#151a23',

  // Borders
  border: 'rgba(255,255,255,0.06)',
  borderGold: 'rgba(252,213,53,0.25)',

  // Accent
  gold: '#FCD535',
  goldDim: '#f0b90b',
  goldGlow: 'rgba(252,213,53,0.15)',

  // Semantic
  green: '#0ecb81',    // Positive, lucro
  red: '#f6465d',      // Negative, perda
  blue: '#3b82f6',     // Info, ready
  muted: '#848e9c',    // Disabled, secondary
}
```

### Tipografia

```typescript
const typography = {
  fonts: {
    ui: 'Geist Sans, system-ui, sans-serif',
    mono: 'JetBrains Mono, monospace',
  },
  sizes: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem',// 30px
  }
}
```

### Componentes

#### Button Variants
```typescript
const buttonVariants = {
  primary: 'bg-gold text-black hover:bg-gold-dim',
  secondary: 'bg-transparent border border-gold text-gold',
  ghost: 'hover:bg-hover',
  danger: 'bg-red/20 text-red hover:bg-red/30',
}
```

#### Card Styles
```css
.glass {
  background: rgba(15, 19, 25, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
}
```

---

## 📄 Tipos TypeScript

### OpportunityItemV2

```typescript
// types/opportunity.ts

export type CapacityBand = 'GREEN' | 'YELLOW' | 'RED'

export type OpStatus =
  | 'ACTIVE'
  | 'READY'
  | 'OBSERVATION_ONLY'
  | 'KILLED'
  | 'DEGRADED'

export interface OpportunityItemV2 {
  // Identidade
  id: string
  symbol: string
  pair: string
  exchange_spot: string
  exchange_futures: string
  is_cross_venue: boolean

  // Preços
  price_spot: number
  price_futures: number

  // Spread
  spread_exec_pct: number
  spread_net_pct: number

  // ROI e Capacidade
  roi_net_pct: number
  profit_usd: number
  capacity_pct: number
  capacity_band: CapacityBand
  entry_leg_usd: number

  // Liquidez
  spot_top_book_usd: number
  futures_top_book_usd: number
  volume_24h_usd: number

  // Funding
  funding_rate: number
  funding_interval_hours: number
  next_funding_at: number | null

  // Execução
  orders_to_fill_spot: number
  orders_to_fill_fut: number
  fill_status: string

  // Score e Status
  score: number
  trust_score: number
  quality_level: string
  status: OpStatus
  execution_decision: string
  kill_reason: string | null

  // Meta
  persistence_minutes: number
  tags: string[]
  ts_created: number
  ts_updated: number
}

export interface SSEPayload {
  items: OpportunityItemV2[]
  meta: {
    cycle_id: number
    ts: number
    counts: {
      total: number
      active: number
      obs: number
      killed: number
    }
    pipeline_latency_ms: number
  }
}
```

### UserSettings

```typescript
// types/settings.ts

export interface UserSettings {
  profile_name: string
  min_spread_pct: number
  min_score: number
  min_volume_usd: number
  min_persistence_min: number
  bankroll_usd: number
  hedge_pct: number
  entry_min_usd: number
  entry_max_usd: number
  hide_blocked: boolean
  allow_cross: boolean
  allow_same: boolean
  spots: string[]
  futures: string[]
  blocked_coins: string[]
}
```

---

## 🔄 Hooks Personalizados

### useOpportunities

```typescript
// hooks/useOpportunities.ts

import { create } from 'zustand'

interface OpportunitiesState {
  items: OpportunityItemV2[]
  meta: SSEPayload['meta'] | null
  loading: boolean
  error: string | null

  // Actions
  setOpportunities: (items: OpportunityItemV2[]) => void
  setMeta: (meta: SSEPayload['meta']) => void
  clear: () => void
}

export const useOpportunities = create<OpportunitiesState>((set) => ({
  items: [],
  meta: null,
  loading: true,
  error: null,

  setOpportunities: (items) => set({ items, loading: false }),
  setMeta: (meta) => set({ meta }),
  clear: () => set({ items: [], meta: null }),
}))
```

### useFilters

```typescript
// hooks/useFilters.ts

export function useFilters() {
  const [minSpread, setMinSpread] = useState(0.5)
  const [minScore, setMinScore] = useState(50)
  const [activeSpots, setActiveSpots] = useState<string[]>(['binance', 'mexc'])
  const [activeFutures, setActiveFutures] = useState<string[]>(['binance_futures'])
  const [searchTerm, setSearchTerm] = useState('')

  const reset = () => {
    setMinSpread(0.5)
    setMinScore(50)
    setSearchTerm('')
  }

  return {
    minSpread,
    setMinSpread,
    minScore,
    setMinScore,
    activeSpots,
    setActiveSpots,
    activeFutures,
    setActiveFutures,
    searchTerm,
    setSearchTerm,
    reset,
  }
}
```

---

## 📡 API Integration

### SSE Connection

```typescript
// lib/sse.ts

export function connectToOpportunities(
  onData: (data: SSEPayload) => void,
  onError?: (error: Event) => void
) {
  const eventSource = new EventSource('/api/sse/opportunities')

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    onData(data)
  }

  eventSource.onerror = (error) => {
    console.error('SSE Error:', error)
    onError?.(error)
    eventSource.close()
  }

  return () => eventSource.close()
}
```

### API Client

```typescript
// lib/api.ts

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ''

export async function fetchSettings(): Promise<UserSettings> {
  const res = await fetch(`${API_BASE}/api/v1/settings`)
  if (!res.ok) throw new Error('Failed to fetch settings')
  return res.json()
}

export async function updateSettings(
  settings: Partial<UserSettings>
): Promise<UserSettings> {
  const res = await fetch(`${API_BASE}/api/v1/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  })
  if (!res.ok) throw new Error('Failed to update settings')
  return res.json()
}

export async function fetchPnLHistory(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/v1/pnl`)
  if (!res.ok) throw new Error('Failed to fetch PnL')
  return res.json()
}
```

---

## 🧩 Componentes Principais

### OpportunitiesTable

```typescript
// components/opportunities/OpportunitiesTable.tsx

interface OpportunitiesTableProps {
  data: OpportunityItemV2[]
  onExecute?: (opp: OpportunityItemV2) => void
  onViewDetails?: (opp: OpportunityItemV2) => void
  onKill?: (opp: OpportunityItemV2) => void
}

export function OpportunitiesTable({
  data,
  onExecute,
  onViewDetails,
  onKill
}: OpportunitiesTableProps) {
  return (
    <table className="w-full">
      <thead>
        <tr>
          <th>Score</th>
          <th>Ativo</th>
          <th>Spread</th>
          <th>ROI</th>
          <th>Capacidade</th>
          <th>Exchanges</th>
          <th>Volume</th>
          <th>Funding</th>
          <th>Status</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        {data.map((opp) => (
          <OpportunityRow
            key={opp.id}
            opp={opp}
            onExecute={onExecute}
            onViewDetails={onViewDetails}
            onKill={onKill}
          />
        ))}
      </tbody>
    </table>
  )
}
```

### KpiCard

```typescript
// components/dashboard/KpiCard.tsx

interface KpiCardProps {
  title: string
  value: string | number
  change?: string
  icon: React.ReactNode
  trend?: 'up' | 'down' | 'neutral'
}

export function KpiCard({
  title,
  value,
  change,
  icon,
  trend = 'neutral'
}: KpiCardProps) {
  return (
    <div className="glass rounded-xl p-6 border border-border">
      <div className="flex items-center justify-between mb-4">
        <span className="text-muted text-sm">{title}</span>
        <div className="text-gold">{icon}</div>
      </div>
      <div className="text-3xl font-bold font-mono text-white">
        {value}
      </div>
      {change && (
        <div className={`text-sm ${
          trend === 'up' ? 'text-green' :
          trend === 'down' ? 'text-red' : 'text-muted'
        }`}>
          {change}
        </div>
      )}
    </div>
  )
}
```

### Sidebar

```typescript
// components/layout/Sidebar.tsx

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Spot x Futuros', href: '/spot-futuros', icon: TrendingUp },
  { name: 'Histórico', href: '/historico', icon: History },
  { name: 'Configurações', href: '/configuracoes', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const [isOpen, setIsOpen] = useState(false)

  return (
    <aside className="fixed top-0 left-0 h-full w-64 bg-surface border-r border-border-gold">
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold text-gradient-gold">DomCrypto</h1>
      </div>

      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg ${
                isActive
                  ? 'bg-gold-glow border-l-[3px] border-gold text-gold'
                  : 'hover:bg-hover border-l-[3px] border-transparent'
              }`}
            >
              <item.icon size={20} />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
```

---

## 📱 Páginas

### Dashboard (/dashboard)

**Responsabilidade:** Visão geral do sistema com KPIs.

**Componentes:**
- KpiBar (4 cards)
- PipelineStatus
- TopOpportunities (top 10)

**Dados:**
- Oportunidades ativas
- Melhor spread
- Spread médio
- Volume total
- Status do sistema

### Spot x Futuros (/spot-futuros)

**Responsabilidade:** Tabela completa de oportunidades.

**Componentes:**
- OpportunitiesTable
- FilterDrawer
- Toolbar (pause, filtros)

**Features:**
- Filtros por spread, score, exchanges
- Busca por símbolo
- Pausar/retomar updates
- Ações rápidas (ver, executar, descartar)

### Histórico (/historico)

**Responsabilidade:** Histórico de trades e PnL.

**Componentes:**
- PnLTable
- PipelineSnapshots
- EquityCurve (chart)

**Dados:**
- Trades fechados
- PnL acumulado
- Snaphots do pipeline

### Configurações (/configuracoes)

**Responsabilidade:** Configurações do usuário.

**Componentes:**
- SettingsForm
- ExchangeSelector
- RiskSettings
- ProfileSelector

**Configurações:**
- Spreads mínimos
- Score mínimo
- Exchanges ativas
- Limites de risco

---

## 🧪 Testes

```bash
# Rodar testes
npm run test

# Testes unitários
npm run test:unit

# Coverage
npm run test -- --coverage
```

### Estrutura de Testes

```
tests/
├── components/
│   ├── OpportunitiesTable.test.tsx
│   ├── KpiCard.test.tsx
│   └── Sidebar.test.tsx
├── hooks/
│   ├── useOpportunities.test.ts
│   └── useFilters.test.ts
├── utils/
│   ├── formatters.test.ts
│   └── constants.test.ts
└── e2e/
    └── dashboard.spec.ts
```

### Exemplo de Teste

```typescript
// components/__tests__/KpiCard.test.tsx

import { render, screen } from '@testing-library/react'
import { KpiCard } from '../KpiCard'
import { TrendingUp } from 'lucide-react'

describe('KpiCard', () => {
  it('renders correctly', () => {
    render(
      <KpiCard
        title="Oportunidades Ativas"
        value={12}
        icon={<TrendingUp />}
      />
    )

    expect(screen.getByText('Oportunidades Ativas')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
  })

  it('shows trend correctly', () => {
    const { rerender } = render(
      <KpiCard
        title="Spread"
        value={1.5}
        change="+0.5%"
        trend="up"
        icon={<TrendingUp />}
      />
    )

    expect(screen.getByText('+0.5%')).toHaveClass('text-green')

    rerender(
      <KpiCard
        title="Spread"
        value={0.5}
        change="-0.2%"
        trend="down"
        icon={<TrendingUp />}
      />
    )

    expect(screen.getByText('-0.2%')).toHaveClass('text-red')
  })
})
```

---

## 🚀 Comandos

```bash
# Desenvolvimento
npm run dev

# Build produção
npm run build

# Start produção
npm start

# Lint
npm run lint

# Type check
npm run type-check

# Testes
npm run test
```

---

## 📈 Performance Targets

| Métrica | Target |
|---------|--------|
| First Contentful Paint | < 1.5s |
| Time to Interactive | < 3.0s |
| First Input Delay | < 100ms |
| Cumulative Layout Shift | < 0.1 |
| Lighthouse Score | > 90 |

### Otimizações

- ✅ Server Components para páginas estáticas
- ✅ Dynamic para páginas com SSE
- ✅ Lazy loading de componentes
- ✅ Image optimization
- ✅ Font optimization
- ✅ Code splitting por rota

---

## 🔐 Variáveis de Ambiente

```bash
# App
NODE_ENV=development
PORT=3000

# API
NEXT_PUBLIC_API_URL=http://localhost:8000
PYTHON_WS_URL=ws://localhost:8000/ws/opportunities

# Database (para API routes)
DATABASE_URL=postgresql://domcrypto:password@localhost:5432/domcrypto
```
