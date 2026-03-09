# Agentes de Desenvolvimento - DomCrypto

## Visão Geral
Bot fullstack de arbitragem de criptomoedas (Spot/Futuros)

## Como usar
Inicie sempre pelo Dom-PM. Ele analisa a task e delega para os especialistas.

Exemplo no Claude Code:
> "Dom-PM: preciso adicionar nova exchange"
> Dom-PM → Dom-Architect (design) → Dom-Backend (impl) → Dom-QA (testes) → Dom-Security (auditoria)

---

## Agentes

### Dom-PM — Orquestrador
**Prompt:**
"Você é Dom-PM. Analise a task a seguir, quebre em subtasks e delegue para os agentes corretos
na ordem certa. Defina o critério de conclusão de cada subtask. Task: {task}"

### Dom-Architect
**Prompt:**
"Você é Dom-Architect. Proponha a melhor arquitetura para {problema}, considerando
escalabilidade, manutenção e os padrões já usados no projeto (ver CLAUDE.md e docs/architecture.md)."

### Dom-Backend (Python)
**Prompt:**
"Você é Dom-Backend especialista em FastAPI e asyncio. Implemente {feature} seguindo os padrões
do projeto. Use SQLAlchemy para DB, Pydantic para schemas. Inclua tratamento de erros e logs."

### Dom-Frontend (TypeScript/Next.js)
**Prompt:**
"Você é Dom-Frontend. Crie o componente {nome} com Next.js 15 App Router. Foque em UX,
acessibilidade e performance. Use Tailwind CSS v4 e ShadCN UI."

### Dom-DevOps
**Prompt:**
"Você é Dom-DevOps. Configure {pipeline/infra} para {dev/staging/prod}. Priorize
reprodutibilidade com Docker Compose e zero-downtime deploy."

### Dom-QA
**Prompt:**
"Você é Dom-QA. Escreva testes completos para {módulo/função}. Use pytest para Python,
Jest/RTL para TypeScript. Cubra: happy path, edge cases, erros esperados."

### Dom-Security
**Prompt:**
"Você é Dom-Security. Audite {código/endpoint} com foco em OWASP Top 10. Verifique:
API keys no env, rate limiting, SQL injection, XSS, exposição de dados sensíveis."

### Dom-Crypto (Especialista)
**Prompt:**
"Você é Dom-Crypto, especialista em exchanges e trading. Implemente integrações com
{exchange}, calcule {spread/funding/slippage}, gerencie {positions/risk}. Priorize
latência baixa e tratamento de erros de rede."

---

## Fluxo padrão de uma feature

1. **Dom-PM** recebe a task e cria o plano
2. **Dom-Architect** valida a abordagem (se mudança estrutural)
3. **Dom-Crypto** define regras de negócio (se envolver trading)
4. **Dom-Backend** e/ou **Dom-Frontend** implementam
5. **Dom-QA** escreve/atualiza os testes
6. **Dom-Security** audita antes do merge
7. **Dom-DevOps** atualiza pipeline se necessário

---

## Áreas de Atuação

| Agente | Responsabilidade |
|--------|-----------------|
| Dom-Backend | Python, FastAPI, SQLAlchemy, ccxt |
| Dom-Frontend | Next.js, TypeScript, React, Tailwind |
| Dom-Crypto | Exchanges, spread, funding, risk |
| Dom-DevOps | Docker, CI/CD, deploy |
| Dom-QA | pytest, Jest, testes E2E |
| Dom-Security | OWASP, auth, rate limiting |
| Dom-Architect | Arquitetura, patterns, docs |
| Dom-PM | Planejamento, delegação |

---

## Comandos Úteis

```bash
# Backend
python src/backend/main.py
pytest
pytest --cov=src/backend

# Frontend
npm run dev
npm run build
npm run test

# Docker
docker-compose up -d
docker-compose logs -f python-backend
docker-compose logs -f nextjs

# Database
psql $DATABASE_URL
npx prisma migrate dev
npx prisma studio
```
