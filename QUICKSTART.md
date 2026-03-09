# Quickstart - DomCrypto

## Início Rápido (5 minutos)

### 1. Instalar Dependências

```bash
cd domcrypto

# Backend Python
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Frontend Next.js
npm install
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas credenciais (opcional para teste)
# BINANCE_API_KEY=
# BINANCE_API_SECRET=
```

### 3. Rodar o Sistema

#### Opção A: Docker (Recomendado)

```bash
docker-compose up -d

# Acessar
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### Opção B: Local

```bash
# Terminal 1 - Backend
python src/backend/main.py

# Terminal 2 - Frontend
npm run dev

# Acessar
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### 4. Verificar Instalação

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

## Estrutura do Sistema

```
domcrypto/
├── Backend Python (FastAPI)
│   ├── Pipeline de oportunidades
│   ├── Integração com exchanges
│   ├── Risk management
│   └── WebSocket para real-time
│
└── Frontend Next.js
    ├── Dashboard com KPIs
    ├── Tabela Spot x Futuros
    ├── Histórico (em implementação)
    └── Configurações (em implementação)
```

## Páginas Disponíveis

| Página | URL | Descrição |
|--------|-----|-----------|
| Home | `/` | Page inicial com links |
| Dashboard | `/dashboard` | KPIs e status do sistema |
| Spot x Futuros | `/spot-futuros` | Tabela de oportunidades |
| Histórico | `/historico` | Em implementação |
| Configurações | `/configuracoes` | Em implementação |

## Funcionalidades

### Dashboard
- Oportunidades ativas
- Melhor spread
- Spread médio
- Volume 24h
- Status do sistema
- Contagem de oportunidades

### Spot x Futuros
- Tabela completa de oportunidades
- Filtros por spread, score, exchanges
- Busca por símbolo
- Pausar/retomar atualizações
- Status badges
- Capacity bands

## Comandos Úteis

```bash
# Backend
python src/backend/main.py           # Rodar backend
pytest                               # Rodar testes
black src/backend/                   # Formatar código

# Frontend
npm run dev                          # Desenvolvimento
npm run build                        # Build produção
npm run lint                         # Lint
npm run type-check                   # TypeScript check

# Docker
docker-compose up -d                 # Iniciar serviços
docker-compose down                  # Parar serviços
docker-compose logs -f               # Ver logs
```

## Troubleshooting

### Erro: "ModuleNotFoundError"
```bash
# Ativar virtualenv e adicionar ao PYTHONPATH
source .venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Erro: "Port already in use"
```bash
# Mude as portas no docker-compose.yml ou .env
PORT=3001
PYTHON_PORT=8001
```

### Frontend não conecta no backend
```bash
# Verifique no .env:
PYTHON_WS_URL=ws://localhost:8000/ws/opportunities
```

## Próximos Passos

1. Configurar API keys das exchanges no `.env`
2. Ajustar parâmetros de risco conforme seu perfil
3. Rodar em modo PAPER_TRADING para testes
4. Monitorar oportunidades no dashboard
5. Implementar histórico e configurações

## Suporte

- Docs: `docs/`
- Architecture: `docs/architecture.md`
- API: `docs/api.md`
- Migration: `MIGRATION.md`
