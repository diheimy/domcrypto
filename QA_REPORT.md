# QA Report - DomCrypto Frontend

**Data:** 2026-03-08
**Versão:** 0.2.1

---

## 📊 Resumo dos Testes

### Testes Unitários (Jest + Testing Library)

| Métrica | Resultado |
|---------|-----------|
| **Suites** | 5 passed, 5 total |
| **Tests** | 102 passed, 102 total |
| **Coverage** | 97.34% (target: 70%) |

### Testes por Categoria

| Categoria | Arquivos | Tests |
|-----------|----------|-------|
| Utils (formatters) | 1 | 52 |
| Components UI (Button) | 1 | 14 |
| Components Dashboard (KpiCard) | 1 | 8 |
| Components Opportunities (ScoreBadge, SpreadCell) | 2 | 28 |

---

## ✅ Testes Implementados

### Utils - Formatters (`tests/unit/utils/formatters.test.ts`)
- `formatUSD()` - 4 testes
- `formatCurrency()` - 2 testes
- `formatPercent()` - 4 testes
- `formatNumber()` - 3 testes
- `formatTime()` - 1 teste
- `formatRelativeTime()` - 4 testes
- `formatFundingRate()` - 2 testes
- `cn()` - 4 testes
- `getCapacityColor()` - 3 testes
- `getCapacityLabel()` - 1 teste
- `getStatusColor()` - 5 testes
- `getStatusLabel()` - 1 teste
- `getScoreColor()` - 3 testes
- `getScoreBg()` - 3 testes
- `getScoreQuality()` - 3 testes
- `getExchangeDisplayName()` - 3 testes
- `isFuturesExchange()` - 2 testes
- `isValidOpportunity()` - 4 testes

### Components - Dashboard (`tests/unit/components/dashboard/KpiCard.test.tsx`)
- Renderização básica
- Valor como string
- Trend up (verde)
- Trend down (vermelho)
- Trend neutral
- Sem change
- Glassmorphism classes
- Border classes

### Components - UI (`tests/unit/components/ui/Button.test.tsx`)
- Renderização com texto
- onClick handler
- Variantes: primary, secondary, ghost, danger, outline
- Tamanhos: sm, md, lg
- Disabled state
- asChild (link)
- Custom className

### Components - Opportunities
#### ScoreBadge (`tests/unit/components/opportunities/ScoreBadge.test.tsx`)
- Score alto (verde, >=70)
- Score médio (amarelo, 50-69)
- Score baixo (vermelho, <50)
- Limites (70, 69, 49)
- Background colors
- Font mono
- Sizes (sm, md, lg)
- showQuality option

#### SpreadCell (`tests/unit/components/opportunities/SpreadCell.test.tsx`)
- Spread positivo (verde)
- Spread negativo (vermelho)
- Spread zero (muted)
- Formatação 2 casas decimais
- showGross option
- Layout flex

---

## 🧪 Testes E2E (Playwright)

### Arquivos Criados
- `tests/e2e/dashboard.spec.ts` - 6 testes
- `tests/e2e/spot-futuros.spec.ts` - 8 testes

### Testes Dashboard
- Carregar dashboard com KPIs
- Mostrar loading inicialmente
- Mostrar top oportunidades
- Navegação pela sidebar
- Status do sistema
- Contagem de oportunidades

### Testes Spot x Futuros
- Mostrar tabela de oportunidades
- Abrir filtro drawer
- Filtrar por spread mínimo
- Pausar/retomar atualizações
- Buscar por símbolo
- Mostrar KPI bar
- Footer com informações
- Status de conexão

---

## 📁 Estrutura de Testes

```
tests/
├── setup.ts                    # Configuração do Jest
├── unit/
│   ├── utils/
│   │   └── formatters.test.ts  # 52 testes
│   └── components/
│       ├── dashboard/
│       │   └── KpiCard.test.tsx    # 8 testes
│       ├── ui/
│       │   └── Button.test.tsx     # 14 testes
│       └── opportunities/
│           ├── ScoreBadge.test.tsx # 16 testes
│           └── SpreadCell.test.tsx # 12 testes
└── e2e/
    ├── dashboard.spec.ts         # 6 testes
    └── spot-futuros.spec.ts      # 8 testes
```

---

## 🔧 Configuração

### Jest (`jest.config.js`)
- ts-jest preset
- jsdom environment
- Module resolution com @/ alias
- Coverage threshold: 70%

### Playwright (`playwright.config.ts`)
- Chromium, Firefox, WebKit
- Base URL: http://localhost:3000
- Screenshot on failure
- Video on failure

### Scripts (`package.json`)
```json
{
  "test": "jest",
  "test:watch": "jest --watch",
  "test:coverage": "jest --coverage",
  "test:e2e": "playwright test",
  "test:e2e:ui": "playwright test --ui"
}
```

---

## 📈 Coverage

### Arquivos Testados
| Arquivo | Coverage |
|---------|----------|
| `src/utils/formatters.ts` | 96.42% |
| `src/components/ui/button.tsx` | 100% |
| `src/components/dashboard/KpiCard.tsx` | 100% |
| `src/components/opportunities/ScoreBadge.tsx` | 100% |
| `src/components/opportunities/SpreadCell.tsx` | 100% |

---

## ✅ Critérios de Aceitação QA-SPEC.md

| Critério | Status |
|----------|--------|
| Testes unitários para nova lógica | ✅ 102 testes |
| Coverage > 70% | ✅ 97.34% |
| Lint passando | ✅ |
| Type check passando | ✅ |
| Build passando | ✅ |

---

## 🚀 Próximos Passos

1. **Expandir testes de componentes** - Adicionar testes para todos componentes
2. **Testes de integração** - Testar hooks e stores
3. **E2E tests** - Executar testes E2E com servidor backend
4. **CI/CD integration** - Adicionar testes ao pipeline
5. **Coverage reports** - Gerar e publicar relatórios de coverage

---

**Comandos:**
```bash
# Rodar testes unitários
npm run test

# Rodar com coverage
npm run test:coverage

# Rodar em watch mode
npm run test:watch

# Rodar E2E tests
npm run test:e2e
```
