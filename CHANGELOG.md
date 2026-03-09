# Changelog

Todas as mudanças notáveis neste projeto.

## [0.2.0] - 2026-03-08 - Migração do DomArb

### Migrado do DomArb
- **Backend Python completo** (150 arquivos)
  - Pipeline de oportunidades
  - Serviços: Fetch, Funding, Quality, Execution, Risk, Analytics
  - API FastAPI com WebSocket
  - Models SQLAlchemy
  - Configuração e settings

- **Documentação**
  - Architecture docs (domarb-architecture-v1.md)
  - Design system (docs/design-system/)
  - API documentation

- **Configurações**
  - requirements.txt
  - .env.example atualizado
  - docker-compose.yml
  - Dockerfiles (Python + Next.js)

### Novos Arquivos
- `prisma/schema.prisma` - Schema do banco de dados
- `pyproject.toml` - Configuração do projeto Python
- `package.json` - Configuração do frontend Next.js
- `tsconfig.json` - Configuração TypeScript
- `next.config.js` - Configuração Next.js
- `.eslintrc.json` - Configuração ESLint
- `run_backend.py` - Script para rodar o backend
- `SETUP.md` - Guia de setup
- `docs/api.md` - Documentação da API

### Atualizados
- `README.md` - Nova estrutura e instruções
- `.claude/CLAUDE.md` - Contexto atualizado
- `AGENTS.md` - Agentes específicos para crypto
- `.env.example` - Variáveis para exchanges
- `requirements-dev.txt` - Todas as dependências
- `CHANGELOG.md` - Historico de mudanças

### Estrutura de Pastas
```
domcrypto/
├── src/
│   ├── backend/          # Código Python migrado
│   │   ├── api/          # Rotas, endpoints
│   │   ├── config/       # Settings
│   │   ├── domain/       # Domain objects
│   │   ├── models/       # SQLAlchemy models
│   │   ├── pipeline/     # Opportunity pipeline
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business services
│   │   └── utils/        # Utilities
│   └── frontend/         # Next.js (a implementar)
├── tests/
├── docs/
├── prisma/
└── scripts/
```

### Notas
- Imports atualizados de `app.` para `src.backend.`
- Settings atualizados para usar variáveis de ambiente do projeto
- Backend pronto para rodar em modo PAPER_TRADING

---

## [0.1.0] - 2026-03-01 - Bootstrap Inicial

### Criado
- Estrutura básica do projeto
- `.claude/CLAUDE.md`
- `AGENTS.md`
- `docs/architecture.md`
- `requirements-dev.txt` (básico)
