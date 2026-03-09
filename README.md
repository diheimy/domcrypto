# dom-crypto

> Bot fullstack de arbitragem de criptomoedas (Spot/Futuros)

## 🚀 Quick Start

### Opção 1: Docker (Recomendado)

```bash
git clone <url>
cd domcrypto
cp .env.example .env
docker-compose up -d

# Acessar:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Opção 2: Local

```bash
# Backend Python
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/backend/main.py

# Frontend Next.js (outro terminal)
npm install
npm run dev
```

Ver [QUICKSTART.md](QUICKSTART.md) para guia completo.

## 📁 Estrutura do Projeto

```
domcrypto/
├── src/
│   ├── backend/              # Python (FastAPI)
│   │   ├── api/              # Rotas, endpoints, adapters
│   │   ├── config/           # Configurações e settings
│   │   ├── domain/           # Domain objects
│   │   ├── models/           # Modelos de dados
│   │   ├── pipeline/         # Pipeline de oportunidades
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Serviços de negócio
│   │   └── utils/            # Utilitários
│   └── frontend/             # Next.js 15 App Router
│       ├── app/              # Pages e API routes
│       ├── components/       # Componentes React
│       └── layout.tsx        # Layout compartilhado
├── tests/
├── docs/
├── prisma/
└── configs...
```

## 🎯 Funcionalidades

### Backend Python
- Pipeline de oportunidades em tempo real
- Integração com exchanges (Binance, Bybit, MEXC, Gate, Bitget, BingX)
- Cálculo de spread, fees, funding
- Risk management integrado
- Paper trading e live trading
- WebSocket para atualizações real-time

### Frontend Next.js
- **Dashboard**: KPIs em tempo real, status do sistema
- **Spot x Futuros**: Tabela completa de oportunidades com filtros
- **Histórico**: Em implementação
- **Configurações**: Em implementação

## 📄 Documentação

| Arquivo | Descrição |
|---------|-----------|
| [QUICKSTART.md](QUICKSTART.md) | Guia de início rápido |
| [SETUP.md](SETUP.md) | Setup detalhado do ambiente |
| [MIGRATION.md](MIGRATION.md) | Histórico da migração domarb → domcrypto |
| [CHANGELOG.md](CHANGELOG.md) | Mudanças e versões |
| [AGENTS.md](AGENTS.md) | Agentes de desenvolvimento |
| [docs/api.md](docs/api.md) | Documentação da API |
| [docs/architecture.md](docs/architecture.md) | Arquitetura do sistema |

## 🔐 Variáveis de Ambiente

Principais variáveis (ver `.env.example`):

```bash
# Exchanges
BINANCE_API_KEY=
BINANCE_API_SECRET=
BYBIT_API_KEY=
BYBIT_API_SECRET=

# Trading
PAPER_TRADING=true
INITIAL_CAPITAL_USD=10000
MIN_SPREAD_PCT=0.5
MIN_SCORE=50

# Database
DATABASE_URL=postgresql://domcrypto:password@localhost:5432/domcrypto
```

## 🛠️ Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11, FastAPI, uvicorn, SQLAlchemy, ccxt |
| Frontend | Next.js 15, TypeScript, React, Tailwind CSS |
| Database | PostgreSQL 16, Prisma ORM |
| Real-time | WebSocket, SSE (Server-Sent Events) |
| Deploy | Docker Compose |

## 📜 Comandos

### Backend
```bash
python src/backend/main.py      # Iniciar backend
pytest                          # Rodar testes
black src/backend/              # Formatar código
```

### Frontend
```bash
npm run dev                     # Desenvolvimento
npm run build                   # Build produção
npm run lint                    # Lint
npm run type-check              # TypeScript check
```

### Docker
```bash
docker-compose up -d            # Iniciar serviços
docker-compose down             # Parar serviços
docker-compose logs -f          # Ver logs
```

## 📊 Páginas

| Página | URL | Status |
|--------|-----|--------|
| Home | `/` | ✅ Pronto |
| Dashboard | `/dashboard` | ✅ Pronto |
| Spot x Futuros | `/spot-futuros` | ✅ Pronto |
| Histórico | `/historico` | 🚧 Em implementação |
| Configurações | `/configuracoes` | 🚧 Em implementação |

## 🔗 Próximos Passos

1. Configurar API keys no `.env`
2. Rodar em modo `PAPER_TRADING=true`
3. Acessar dashboard em http://localhost:3000
4. Implementar histórico e configurações
5. Conectar frontend com backend real

## 📝 License

Proprietário - Todos os direitos reservados.

---

**Author:** Dom
**Version:** 0.2.0
**Last Updated:** 2026-03-08
