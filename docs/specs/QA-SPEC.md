# QA - Especificação de Testes

**DomCrypto** - Plano de Testes e Quality Assurance
Versão: 0.2.0 | Data: 2026-03-08

---

## 📋 Visão Geral

Estratégia de testes para garantir qualidade do sistema de arbitragem.

### Pirâmide de Testes

```
           ╱█╲
          ╱███╲         E2E (10%)
         ╱█████╲        Testes críticos de usuário
        ╱███████╲
       ╱─────────╲
      ╱███████████╲      Integration (20%)
     ╱█████████████╲     Testes de API, serviços
    ╱─────────────────╲
   ╱███████████████████╲   Unit (70%)
  ╱█████████████████████╲  Testes de funções, métodos
 ╱───────────────────────╲
```

---

## 🧪 Testes Unitários (Backend Python)

### Estrutura

```
tests/
└── unit/
    ├── test_spread_engine.py
    ├── test_quality_engine.py
    ├── test_risk_engine.py
    ├── test_opportunity_builder.py
    ├── test_hard_rules.py
    ├── test_normalizer.py
    ├── test_fee_engine.py
    ├── test_funding_engine.py
    └── test_capital_allocation.py
```

### Exemplos de Testes

```python
# tests/unit/test_spread_engine.py

import pytest
from src.backend.models.spread_engine import SpreadCalculator

class TestSpreadCalculator:
    @pytest.fixture
    def calculator(self):
        return SpreadCalculator()

    def test_calculate_gross_spread(self, calculator):
        """Testa cálculo de spread bruto."""
        spot_price = 100.0
        futures_price = 101.5

        expected = 1.5  # (101.5 - 100) / 100 * 100
        result = calculator.calculate_gross_spread(spot_price, futures_price)

        assert result == pytest.approx(expected, rel=0.01)

    def test_calculate_net_spread_with_fees(self, calculator):
        """Testa cálculo de spread líquido com fees."""
        gross_spread = 2.0
        fee_pct = 0.2

        expected = 1.6  # 2.0 - (0.2 * 2)
        result = calculator.calculate_net_spread(gross_spread, fee_pct)

        assert result == pytest.approx(expected, rel=0.01)

    def test_negative_spread(self, calculator):
        """Testa spread negativo (futures < spot)."""
        spot_price = 100.0
        futures_price = 99.0

        result = calculator.calculate_gross_spread(spot_price, futures_price)

        assert result < 0
```

```python
# tests/unit/test_quality_engine.py

import pytest
from src.backend.services.quality.quality_engine import QualityEngine
from src.backend.domain.opportunity_dto import OpportunityDTO

class TestQualityEngine:
    @pytest.fixture
    def engine(self):
        return QualityEngine()

    def test_high_score_for_high_spread(self, engine):
        """Oportunidades com alto spread devem ter score alto."""
        opp = OpportunityDTO(
            symbol="BTC",
            spread_net_pct=3.0,
            volume_24h_usd=1000000,
            spot_top_book_usd=50000,
            futures_top_book_usd=50000,
        )

        score = engine.calculate_score(opp)

        assert score >= 70
        assert score <= 100

    def test_low_score_for_low_volume(self, engine):
        """Volume baixo deve reduzir score."""
        opp = OpportunityDTO(
            symbol="ALTCOIN",
            spread_net_pct=2.0,
            volume_24h_usd=10000,  # Baixo volume
            spot_top_book_usd=100,
            futures_top_book_usd=100,
        )

        score = engine.calculate_score(opp)

        assert score < 50

    def test_capacity_band_calculation(self, engine):
        """Testa cálculo de banda de capacidade."""
        opp_green = OpportunityDTO(capacity_pct=80, entry_leg_usd=100)
        opp_yellow = OpportunityDTO(capacity_pct=50, entry_leg_usd=100)
        opp_red = OpportunityDTO(capacity_pct=10, entry_leg_usd=100)

        assert engine.calculate_capacity_band(opp_green) == "GREEN"
        assert engine.calculate_capacity_band(opp_yellow) == "YELLOW"
        assert engine.calculate_capacity_band(opp_red) == "RED"
```

```python
# tests/unit/test_hard_rules.py

import pytest
from src.backend.pipeline.hard_rules import HardRulesFilter
from src.backend.domain.opportunity_dto import OpportunityDTO

class TestHardRulesFilter:
    @pytest.fixture
    def filter_rules(self):
        return HardRulesFilter(
            min_spread_pct=0.5,
            min_score=50,
            min_volume_usd=100000,
        )

    def test_passes_all_rules(self, filter_rules):
        """Oportunidade deve passar em todas as regras."""
        opp = OpportunityDTO(
            symbol="BTC",
            spread_net_pct=1.5,
            score=75,
            volume_24h_usd=500000,
            status="ACTIVE",
        )

        assert filter_rules.should_include(opp) is True

    def test_fails_spread_rule(self, filter_rules):
        """Spread abaixo do mínimo deve falhar."""
        opp = OpportunityDTO(
            symbol="BTC",
            spread_net_pct=0.3,  # Abaixo de 0.5
            score=75,
            volume_24h_usd=500000,
        )

        assert filter_rules.should_include(opp) is False

    def test_blocked_exchanges(self, filter_rules):
        """Exchange bloqueada deve falhar."""
        filter_rules.add_blocked_exchange("binance")

        opp = OpportunityDTO(
            symbol="BTC",
            exchange_spot="binance",
            spread_net_pct=1.5,
            score=75,
            volume_24h_usd=500000,
        )

        assert filter_rules.should_include(opp) is False
```

---

## 🔗 Testes de Integração (Backend Python)

### Estrutura

```
tests/
└── integration/
    ├── test_fetch_service.py
    ├── test_pipeline.py
    ├── test_persistence.py
    ├── test_websocket.py
    └── test_api_endpoints.py
```

### Exemplos de Testes

```python
# tests/integration/test_pipeline.py

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from src.backend.pipeline.opportunity_pipeline import OpportunityPipeline
from src.backend.services.fetch.fetch_service import FetchService

class TestOpportunityPipeline:
    @pytest.fixture
    def pipeline(self):
        return OpportunityPipeline()

    @pytest.mark.asyncio
    async def test_full_pipeline_execution(self, pipeline):
        """Testa execução completa do pipeline."""
        # Mock fetch service
        with patch.object(pipeline, 'fetch_service', spec=FetchService) as mock_fetch:
            mock_fetch.fetch_all.return_value = {
                'tickers': [...],
                'orderbooks': [...],
            }

            # Executar ciclo
            result = await pipeline.run_cycle()

            # Verificar resultado
            assert len(result) > 0
            assert all(opp.score > 0 for opp in result)

    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self, pipeline):
        """Testa tratamento de erro no pipeline."""
        with patch.object(pipeline, 'fetch_service') as mock_fetch:
            mock_fetch.fetch_all.side_effect = Exception("API Error")

            # Pipeline deve lidar com erro graciosamente
            result = await pipeline.run_cycle()

            assert result == []
```

```python
# tests/integration/test_api_endpoints.py

import pytest
from httpx import AsyncClient
from src.backend.main import app

class TestAPIEndpoints:
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Testa health check endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_get_opportunities(self):
        """Testa endpoint de oportunidades."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/opportunities")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "meta" in data

    @pytest.mark.asyncio
    async def test_get_settings(self):
        """Testa endpoint de configurações."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/settings")

            assert response.status_code == 200
            data = response.json()
            assert "profile_name" in data
            assert "min_spread_pct" in data
```

---

## 🌐 Testes E2E (Frontend)

### Estrutura

```
tests/
└── e2e/
    ├── dashboard.spec.ts
    ├── spot-futuros.spec.ts
    ├── configuracoes.spec.ts
    └── fixtures.ts
```

### Exemplos de Testes (Playwright)

```typescript
// tests/e2e/dashboard.spec.ts

import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test('deve carregar dashboard com KPIs', async ({ page }) => {
    await page.goto('/dashboard')

    // Verificar KPIs
    await expect(page.getByText('Oportunidades Ativas')).toBeVisible()
    await expect(page.getByText('Melhor Spread')).toBeVisible()
    await expect(page.getByText('Spread Médio')).toBeVisible()
    await expect(page.getByText('Volume 24h Total')).toBeVisible()

    // Verificar status do sistema
    await expect(page.getByText('Status do Sistema')).toBeVisible()
  })

  test('deve mostrar loading inicialmente', async ({ page }) => {
    await page.goto('/dashboard')

    // Verificar loading state
    await expect(page.getByText('Carregando')).toBeVisible()

    // Aguardar dados carregarem
    await expect(page.getByTestId('kpi-cards')).toBeVisible({ timeout: 10000 })
  })

  test('deve atualizar dados em tempo real', async ({ page }) => {
    await page.goto('/dashboard')

    // Capturar valor inicial
    const initialActiveOpps = await page.getByTestId('active-opportunities').textContent()

    // Aguardar atualização (SSE)
    await page.waitForTimeout(5000)

    // Verificar se atualizou
    const updatedActiveOpps = await page.getByTestId('active-opportunities').textContent()
    expect(updatedActiveOpps).not.toBe(initialActiveOpps)
  })
})
```

```typescript
// tests/e2e/spot-futuros.spec.ts

import { test, expect } from '@playwright/test'

test.describe('Spot x Futuros', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/spot-futuros')
  })

  test('deve mostrar tabela de oportunidades', async ({ page }) => {
    // Verificar cabeçalhos da tabela
    await expect(page.getByText('Score')).toBeVisible()
    await expect(page.getByText('Spread')).toBeVisible()
    await expect(page.getByText('ROI')).toBeVisible()
    await expect(page.getByText('Exchanges')).toBeVisible()

    // Verificar dados na tabela
    const rows = await page.locator('tbody tr').count()
    expect(rows).toBeGreaterThan(0)
  })

  test('deve filtrar por spread mínimo', async ({ page }) => {
    // Abrir filtros
    await page.getByText('Filtros').click()

    // Ajustar spread mínimo
    await page.locator('input[type="range"]').first().fill('2')

    // Verificar filtragem
    const spreadCells = await page.locator('td:textContaining("%")').all()
    for (const cell of spreadCells) {
      const value = await cell.textContent()
      expect(parseFloat(value)).toBeGreaterThanOrEqual(2.0)
    }
  })

  test('deve pausar/retomar atualizações', async ({ page }) => {
    // Clicar em pausar
    await page.getByText('Executando').click()

    // Verificar estado pausado
    await expect(page.getByText('Pausado')).toBeVisible()

    // Clicar em retomar
    await page.getByText('Pausado').click()

    // Verificar estado ativo
    await expect(page.getByText('Executando')).toBeVisible()
  })

  test('deve buscar por símbolo', async ({ page }) => {
    // Digitar busca
    await page.locator('input[placeholder*="BTC"]').fill('ETH')

    // Aguardar filtragem
    await page.waitForTimeout(500)

    // Verificar resultados
    const rows = await page.locator('tbody tr').all()
    for (const row of rows) {
      await expect(row).toContainText('ETH')
    }
  })
})
```

---

## 📊 Métricas de Qualidade

### Coverage Targets

| Tipo | Target |
|------|--------|
| Backend (Python) | > 80% |
| Frontend (TS) | > 70% |
| Crítico | > 90% |

### Quality Gates

```yaml
# .github/workflows/ci.yml

quality_gates:
  tests:
    min_coverage: 80
    max_failures: 0

  lint:
    black: pass
    flake8: pass
    mypy: pass
    eslint: pass

  security:
    bandit: pass
    audit: pass
```

---

## 🔒 Testes de Segurança

### Backend

```python
# tests/security/test_api_security.py

import pytest
from httpx import AsyncClient

class TestAPISecurity:
    @pytest.mark.asyncio
    async def test_no_sql_injection(self):
        """Testa prevenção contra SQL injection."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            malicious_input = "'; DROP TABLE opportunities; --"
            response = await ac.get(f"/api/v1/opportunities?symbol={malicious_input}")

            # Deve retornar 400 ou filtrar input
            assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Testa rate limiting."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Fazer muitas requisições rápidas
            responses = []
            for _ in range(100):
                response = await ac.get("/health")
                responses.append(response.status_code)

            # Algumas devem ser limitadas (429)
            assert 429 in responses
```

### Frontend

```typescript
// tests/security/xss.test.tsx

import { render, screen } from '@testing-library/react'
import { OpportunitiesTable } from '@/components/opportunities/OpportunitiesTable'

describe('XSS Prevention', () => {
  it('deve escapar HTML em dados de oportunidade', () => {
    const maliciousOpp = [{
      id: '<script>alert("XSS")</script>',
      symbol: 'BTC"><img src=x onerror=alert(1)>',
      spread_net_pct: 1.5,
      // ... outros campos
    }]

    render(<OpportunitiesTable data={maliciousOpp} />)

    // HTML malicioso deve ser escaped
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })
})
```

---

## 🚀 Pipeline de CI/CD

```yaml
# .github/workflows/ci.yml

name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Lint
        run: |
          black src/backend/ --check
          flake8 src/backend/
          mypy src/backend/

      - name: Test
        run: pytest --cov=src/backend --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Test
        run: npm test -- --coverage

      - name: Build
        run: npm run build

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4

      - name: Install Playwright
        run: npx playwright install

      - name: Run E2E tests
        run: npx playwright test
```

---

## 📝 Checklist de QA

### Pull Request Checklist

```markdown
## QA Checklist

### Código
- [ ] Código segue style guide
- [ ] Type hints adicionados (Python/TS)
- [ ] Sem `console.log` ou `print` de debug

### Testes
- [ ] Testes unitários para nova lógica
- [ ] Testes de integração para APIs
- [ ] Coverage não diminuiu

### Segurança
- [ ] Input validation adicionada
- [ ] Sem secrets no código
- [ ] SQL injection prevenido

### Performance
- [ ] Sem N+1 queries
- [ ] Cache onde apropriado
- [ ] Big O considerado

### Documentação
- [ ] Docstrings atualizadas
- [ ] README atualizado se necessário
- [ ] CHANGELOG atualizado
```

---

## 🛠️ Ferramentas

### Backend Python
| Ferramenta | Uso |
|-----------|-----|
| pytest | Test runner |
| pytest-asyncio | Testes async |
| pytest-cov | Coverage |
| black | Formatter |
| flake8 | Linter |
| mypy | Type checker |
| bandit | Security scanner |

### Frontend TypeScript
| Ferramenta | Uso |
|-----------|-----|
| Jest | Test runner |
| Testing Library | Component tests |
| Playwright | E2E tests |
| ESLint | Linter |
| Prettier | Formatter |
| TypeScript | Type checker |

---

## 📈 Reports

### Gerar Reports

```bash
# Backend
pytest --cov=src/backend --cov-report=html
# Abre: open htmlcov/index.html

# Frontend
npm test -- --coverage
# Abre: open coverage/index.html

# E2E
npx playwright test --reporter=html
# Abre: npx playwright show-report
```

---

## 🎯 Critérios de Aceitação

### Para uma Feature ser "Done"

1. ✅ Código implementado e funcional
2. ✅ Testes unitários passando (>80% coverage)
3. ✅ Testes de integração passando
4. ✅ Lint e type check passando
5. ✅ E2E tests passando (se aplicável)
6. ✅ Documentação atualizada
7. ✅ Code review aprovado
8. ✅ Security scan limpo
