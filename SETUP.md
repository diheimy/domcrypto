# Setup Guide - DomCrypto

Guia completo para configurar o ambiente de desenvolvimento.

## Pré-requisitos

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+ (ou Docker)
- Git

## Opção 1: Setup com Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd domcrypto

# 2. Copie as variáveis de ambiente
cp .env.example .env

# 3. Edite .env com suas credenciais
# - BINANCE_API_KEY, BINANCE_API_SECRET
# - BYBIT_API_KEY, BYBIT_API_SECRET

# 4. Suba os serviços
docker-compose up -d

# 5. Verifique os logs
docker-compose logs -f python-backend
docker-compose logs -f nextjs

# 6. Acesse
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## Opção 2: Setup Local (Desenvolvimento)

### Backend Python

```bash
# 1. Crie virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Instale dependências
pip install -r requirements-dev.txt

# 3. Copie variáveis de ambiente
cp .env.example .env

# 4. Execute o backend
python src/backend/main.py

# Ou use o script de run
python run_backend.py
```

### Frontend Next.js

```bash
# 1. Instale dependências
npm install

# 2. Copie variáveis de ambiente
cp .env.example .env

# 3. Execute em modo desenvolvimento
npm run dev

# 4. Acesse http://localhost:3000
```

### Database

```bash
# Opção A: Docker
docker run -d \
  --name domcrypto-db \
  -e POSTGRES_DB=domcrypto \
  -e POSTGRES_USER=domcrypto \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:16-alpine

# Opção B: Local
# Crie o database manualmente
createdb -U postgres domcrypto

# Rodar migrations (se usando Prisma)
npx prisma migrate dev
npx prisma generate
```

## Verificação do Setup

### Backend
```bash
# Testar health check
curl http://localhost:8000/health

# Deve retornar: {"status":"healthy"}
```

### Frontend
```bash
# Verificar build
npm run build

# Rodar testes
npm run test
```

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'src'"
Adicione a raiz do projeto ao PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
# Windows: set PYTHONPATH=%PYTHONPATH%;%cd%\src
```

### Erro: "Connection refused" no PostgreSQL
Verifique se o banco está rodando:
```bash
docker ps | grep postgres
# ou
pg_isready -h localhost -p 5432
```

### Erro: "Port already in use"
Mude as portas no `docker-compose.yml` ou `.env`:
```
PORT=3001
PYTHON_PORT=8001
```

## Próximos Passos

1. Configure suas API keys no `.env`
2. Execute o backend em modo `PAPER_TRADING=true`
3. Acesse o dashboard em http://localhost:3000
4. Monitore os logs para oportunidades

## Estrutura do Projeto

```
domcrypto/
├── src/
│   ├── backend/      # Python (FastAPI)
│   └── frontend/     # Next.js (a implementar)
├── tests/
├── docs/
├── prisma/
├── docker-compose.yml
└── package.json
```

## Comandos Úteis

```bash
# Backend
python src/backend/main.py
pytest tests/
black src/backend/
flake8 src/backend/

# Frontend
npm run dev
npm run build
npm run lint
npm run type-check

# Docker
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose restart python-backend
```
