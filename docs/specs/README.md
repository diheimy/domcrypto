# Especificações de Desenvolvimento

Índice de documentos de especificação do projeto DomCrypto.

---

## 📚 Documentos Disponíveis

| Documento | Descrição | Status |
|-----------|-----------|--------|
| [BACKEND-SPEC.md](./BACKEND-SPEC.md) | Especificação do Backend Python | ✅ Completo |
| [FRONTEND-SPEC.md](./FRONTEND-SPEC.md) | Especificação do Frontend Next.js | ✅ Completo |
| [QA-SPEC.md](./QA-SPEC.md) | Especificação de Testes e QA | ✅ Completo |

---

## 🗂️ Resumo por Área

### Backend Python (`BACKEND-SPEC.md`)

- **Arquitetura:** Pipeline de oportunidades (ciclo 3s)
- **Endpoints:** HTTP + WebSocket
- **Models:** Opportunity, UserSettings, PnL, Snapshots
- **Serviços:** Fetch, Funding, Quality, Execution, Risk
- **Database:** PostgreSQL com SQLAlchemy
- **Configurações:** Environment variables

### Frontend Next.js (`FRONTEND-SPEC.md`)

- **Stack:** Next.js 14, TypeScript, Tailwind CSS
- **Páginas:** Dashboard, Spot x Futuros, Histórico, Configurações
- **Componentes:** Tabela, KPIs, Filtros, Sidebar
- **Estado:** Zustand + Hooks
- **Real-time:** SSE (Server-Sent Events)
- **Design:** Dark theme com gold accents

### QA (`QA-SPEC.md`)

- **Pirâmide:** Unit (70%), Integration (20%), E2E (10%)
- **Backend:** pytest, pytest-asyncio, coverage
- **Frontend:** Jest, Testing Library, Playwright
- **CI/CD:** GitHub Actions workflows
- **Quality Gates:** Coverage > 80%, lint, type check

---

## 📋 Padrões do Projeto

### Código

```python
# Python - Docstring Google Style
def calculate_spread(spot: float, futures: float) -> float:
    """Calculate gross spread percentage.

    Args:
        spot: Spot market price
        futures: Futures market price

    Returns:
        Spread percentage
    """
    return ((futures - spot) / spot) * 100
```

```typescript
// TypeScript - JSDoc + Type hints
/**
 * Calculate net spread after fees
 */
export function calculateNetSpread(
  grossSpread: number,
  feePct: number
): number {
  return grossSpread - (feePct * 2)
}
```

### Commits

Seguir [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: adicionar cálculo de funding rate
fix: corrigir bug de spread negativo
docs: atualizar README com exemplos
refactor: otimizar query de oportunidades
test: adicionar testes do spread engine
chore: atualizar dependências
```

### Pull Requests

**Título:** `[feat] Adicionar endpoint de PnL history`

**Descrição:**
```markdown
## O que foi feito
- Endpoint GET /api/v1/pnl
- Histórico de trades fechados
- Filtros por período

## Tipo de mudança
- [ ] Bug fix
- [x] Nova feature
- [ ] Breaking change

## Checklist
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Documentação atualizada
- [ ] Code review
```

---

## 🚀 Quick Reference

### Backend

```bash
# Rodar backend
python src/backend/main.py

# Testes
pytest --cov=src/backend

# Code quality
black src/backend/ && flake8 src/backend/ && mypy src/backend/
```

### Frontend

```bash
# Desenvolvimento
npm run dev

# Build
npm run build

# Testes
npm test

# Quality
npm run lint && npm run type-check
```

### Docker

```bash
# Todos os serviços
docker-compose up -d

# Logs
docker-compose logs -f python-backend
docker-compose logs -f nextjs

# Parar
docker-compose down
```

---

## 📞 Suporte

- **Issues:** GitHub Issues
- **Documentação:** `docs/`
- **API Docs:** `http://localhost:8000/docs` (Swagger)
- **Storybook:** `http://localhost:6006` (se configurado)

---

**Última atualização:** 2026-03-08
**Versão:** 0.2.0
