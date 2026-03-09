# 🚀 Deploy Guide - DomCrypto

## Pré-requisitos

- Docker e Docker Compose
- Node.js 20+ (para dev local)
- Python 3.11+ (para dev local)
- PostgreSQL 16+ (ou usar container Docker)

---

## 🐳 Deploy com Docker (Recomendado)

### 1. Configurar variáveis de ambiente

```bash
# Copiar o arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
# - API keys das exchanges
# - Senha do PostgreSQL
# - Configurações de trading
```

### 2. Subir todos os serviços

```bash
docker-compose up -d --build
```

### 3. Verificar logs

```bash
# Logs de todos os serviços
docker-compose logs -f

# Logs específicos
docker-compose logs -f python-backend
docker-compose logs -f nextjs
docker-compose logs -f postgres
```

### 4. Acessar aplicação

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Health Check:** http://localhost:8000/health

### 5. Parar serviços

```bash
docker-compose down
```

### 6. Resetar banco de dados (cuidado!)

```bash
docker-compose down -v  # Remove volumes
```

---

## 💻 Deploy Local (Desenvolvimento)

### 1. Instalar dependências

```bash
# Backend Python
pip install -r requirements.txt

# Frontend Node.js
npm install
```

### 2. Configurar ambiente

```bash
cp .env.example .env
# Editar .env com suas configurações
```

### 3. Iniciar PostgreSQL

```bash
# Usando Docker
docker run -d --name domcrypto_postgres \
  -e POSTGRES_DB=domcrypto \
  -e POSTGRES_USER=domcrypto \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:16-alpine
```

### 4. Iniciar backend Python

```bash
python run_backend.py
# Ou
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Iniciar frontend Next.js

```bash
npm run dev
```

### 6. Acessar

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## ☁️ Deploy em Produção (Cloud)

### Vercel (Frontend)

1. Instalar Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel --prod
```

3. Configurar variáveis de ambiente no dashboard da Vercel

### Backend (Railway/Render/Fly.io)

1. Subir código Python
2. Configurar variáveis de ambiente
3. Adicionar PostgreSQL
4. Deploy automático via Git

### Variáveis necessárias

```env
# Database
DATABASE_URL=postgresql://...

# Exchanges
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
BYBIT_API_KEY=...
BYBIT_API_SECRET=...

# Config
PAPER_TRADING=false
INITIAL_CAPITAL_USD=10000
```

---

## 🧪 Testes antes do deploy

```bash
# Testes unitários
npm run test

# Coverage
npm run test:coverage

# Type check
npm run type-check

# Lint
npm run lint

# Build
npm run build
```

---

## 🔧 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs python-backend
docker-compose logs nextjs

# Reconstruir
docker-compose up -d --build --force-recreate
```

### Erro de conexão com banco

```bash
# Verificar se postgres está saudável
docker-compose ps

# Testar conexão
docker-compose exec postgres pg_isready -U domcrypto
```

### Port already in use

```bash
# Matar processo na porta
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

---

## 📊 Monitoramento

### Health Checks

- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000/health

### Logs em produção

```bash
# Docker
docker-compose logs -f

# Next.js PM2
pm2 logs domcrypto-next

# Python
tail -f logs/domcrypto.log
```

---

## 📝 Checklist de Deploy

- [ ] `.env` configurado com API keys
- [ ] PostgreSQL configurado
- [ ] Testes passando (`npm run test`)
- [ ] Build passando (`npm run build`)
- [ ] Type check passando (`npm run type-check`)
- [ ] Lint passando (`npm run lint`)
- [ ] Variáveis de produção configuradas
- [ ] Backup do banco configurado
- [ ] Logs configurados
- [ ] Monitoramento configurado
