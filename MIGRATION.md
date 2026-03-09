# Migração DomArb → DomCrypto

**Data:** 2026-03-08
**Status:** Completa

## Resumo

Migração completa do projeto `domarb` (bot de arbitragem funcional) para a estrutura do `domcrypto` (novo boilerplate padronizado).

## O que foi migrado

### 1. Backend Python (150 arquivos)
- ✅ `app/` → `src/backend/`
- ✅ Todos os serviços (Fetch, Funding, Quality, Execution, Risk, Analytics)
- ✅ Pipeline de oportunidades
- ✅ API FastAPI + WebSocket
- ✅ Models e schemas
- ✅ Configuração e settings

### 2. Documentação
- ✅ `domarb-architecture-v1.md` → `docs/`
- ✅ `design-system/` → `docs/design-system/`
- ✅ API documentation atualizada

### 3. Configurações
- ✅ `requirements.txt` copiado
- ✅ `requirements-dev.txt` expandido
- ✅ `.env.example` com todas variáveis
- ✅ `docker-compose.yml` criado
- ✅ Dockerfiles (Python + Next.js)

### 4. Testes
- ✅ `tests/test_contract_v1.py` migrado

### 5. Novos Arquivos Criados
- ✅ `prisma/schema.prisma`
- ✅ `pyproject.toml`
- ✅ `package.json` (Next.js)
- ✅ `tsconfig.json`
- ✅ `next.config.js`
- ✅ `.eslintrc.json`
- ✅ `run_backend.py`
- ✅ `SETUP.md`
- ✅ `docs/api.md`

## Ajustes Realizados

### Imports Python
Todos os imports foram atualizados:
```python
# Antes
from app.services.risk.portfolio_state import PortfolioRiskState

# Depois
from src.backend.services.risk.portfolio_state import PortfolioRiskState
```

### Settings
Arquivo `config/settings.py` atualizado para usar variáveis de ambiente do novo projeto:
- `PYTHON_ENV`
- `DATABASE_URL`
- `BINANCE_API_KEY`, `BINANCE_API_SECRET`
- `BYBIT_API_KEY`, `BYBIT_API_SECRET`
- `PAPER_TRADING`
- `INITIAL_CAPITAL_USD`
- Risk settings (stop loss, drawdown, position size)

## Estrutura Final

```
domcrypto/
├── src/
│   ├── backend/              # Python completo (150 arquivos)
│   └── frontend/             # Next.js (vazio, pronto p/ implementar)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── test_contract_v1.py
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── design-system/
├── prisma/
│   └── schema.prisma
├── docker-compose.yml
├── Dockerfile.python
├── Dockerfile.nextjs
├── package.json
├── tsconfig.json
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── README.md
├── SETUP.md
├── CHANGELOG.md
└── AGENTS.md
```

## Próximos Passos

1. **Instalar dependências**
   ```bash
   pip install -r requirements-dev.txt
   npm install
   ```

2. **Configurar .env**
   - Adicionar API keys das exchanges
   - Configurar DATABASE_URL

3. **Rodar migrações do banco**
   ```bash
   npx prisma migrate dev
   ```

4. **Iniciar backend**
   ```bash
   python run_backend.py
   ```

5. **Implementar frontend Next.js**
   - Seguir arquitetura em `docs/architecture.md`
   - Usar design system em `docs/design-system/`
   - Integrar com SSE em `/api/sse/opportunities`

## Checklist de Validação

- [ ] Backend inicia sem erros
- [ ] Conexão com PostgreSQL funciona
- [ ] WebSocket está disponível em `ws://localhost:8000/ws/opportunities`
- [ ] Health check responde em `GET /health`
- [ ] Tests passam (`pytest`, `npm test`)
- [ ] Docker compose sobe todos os serviços

## Notas Técnicas

- Imports relativos dentro do backend foram mantidos
- Módulo `src.backend` registrado via `pyproject.toml`
- Scripts de setup disponíveis em `run_backend.py`
- Ambiente isolado recomendado: `.venv` para Python, `node_modules` para npm
