# dom-crypto — Contexto do Projeto

## Visão geral
Bot fullstack de arbitragem de criptomoedas (Spot/Futuros)

## Stack
- **Language:** Python e TypeScript
- **Backend:** FastAPI, uvicorn, SQLAlchemy, ccxt
- **Frontend:** Next.js 15 (App Router), TypeScript, React
- **Database:** PostgreSQL 16
- **Package Manager:** npm
- **Author:** Dom

## Comandos chave

### Backend Python
- `python src/backend/main.py` → Inicia o backend
- `pip install -r requirements.txt` → Instala dependências
- `pytest` → Roda testes

### Frontend Next.js
- `npm run dev`        → Inicia desenvolvimento
- `npm run build`      → Build de produção
- `npm run test`       → Executa todos os testes
- `npm run test:unit`  → Apenas testes unitários
- `npm run lint`       → Verifica código
- `npm run type-check` → Checa tipos TypeScript

### Docker
- `docker-compose up -d` → Sobe todos os serviços
- `docker-compose down`  → Para todos os serviços

## Padrões do projeto
- TypeScript strict mode habilitado
- Commits seguem Conventional Commits (feat/fix/chore/docs/refactor)
- Testes obrigatórios para qualquer nova feature
- Nunca commitar `.env` — usar apenas `.env.example`
- PRs sempre passam pelo checklist de Dom-Security antes do merge

## Estrutura do projeto

```
domcrypto/
├── src/
│   ├── backend/          # Python (FastAPI)
│   │   ├── api/          # Rotas, endpoints, adapters
│   │   ├── config/       # Configurações e settings
│   │   ├── domain/       # Domain objects
│   │   ├── models/       # Modelos de dados
│   │   ├── pipeline/     # Pipeline de oportunidades
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Serviços de negócio
│   │   ├── static/       # Assets estáticos
│   │   ├── templates/    # Jinja templates
│   │   └── utils/        # Utilitários
│   └── frontend/         # Next.js/TypeScript (a implementar)
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── architecture.md   # Arquitetura do sistema
│   ├── api.md            # Documentação da API
│   └── design-system/    # Design system
├── scripts/
├── .github/workflows/
└── docker-compose.yml
```

## Agentes disponíveis
Ver: docs/agents-config.md

## Skills externas instaladas
- **get-shit-done** - Framework de produtividade e gestão de tasks
- **ui-ux-pro-max-skill** - Skills de UI/UX design
- **awesome-claude-code** - Recursos e templates para Claude Code

## Contexto de negócio
- Bot de arbitragem de criptomoedas operando em Spot e Futuros
- Integração com exchanges: Binance, Bybit, MEXC
- Processamento assíncrono para baixa latência
- Paper trading e live trading
- Risk management integrado

## Estilo de código
- Componentes: PascalCase
- Funções/variáveis: camelCase
- Constantes globais: UPPER_SNAKE_CASE
- Arquivos: kebab-case

## Arquitetura

### Backend Python
- **Pipeline**: Fetch → Normalizer → OpportunityBuilder → HardRules → Scoring
- **Services**: Fetch, Funding, Quality, Execution, Risk, Analytics
- **Persistence**: PostgreSQL com SQLAlchemy
- **Real-time**: WebSocket para frontend

### Frontend Next.js (a implementar)
- **App Router**: Pages em `app/`
- **SSE**: Server-Sent Events para oportunidades
- **Components**: `components/` com ShadCN UI
- **Hooks**: Custom hooks em `hooks/`
