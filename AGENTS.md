# AGENTS.md — Project Bootstrap Template
> **Como usar:** Coloque este arquivo na raiz do novo projeto e diga ao Claude Code:  
> _"Execute o AGENTS.md e prepare o ambiente do projeto."_

---

## 🧠 INSTRUÇÕES PARA O AGENTE

Você é o **agente de bootstrap** deste projeto. Leia este arquivo do início ao fim e execute **todas as etapas em ordem**. Ao final, o ambiente deve estar 100% pronto para desenvolvimento.

**Regras de execução:**
- Confirme cada etapa com ✅ antes de prosseguir
- Se houver erro, resolva antes de continuar
- Use `/clear` entre blocos pesados para resetar contexto
- Ao final, gere o relatório de conclusão da Seção 12
- Não pergunte — execute. Se tiver dúvida, escolha o padrão mais seguro.

---

## 📋 SEÇÃO 1 — IDENTIDADE DO PROJETO

> ⚠️ **Preencha antes de executar**

```yaml
project_name: "dom-crypto"             # Nome atualizado para a versão do motor
project_description: "Bot fullstack de arbitragem de criptomoedas (Spot/Futuros)"
project_type: "web-app"             # Reflete a união do Backend (V112) e Frontend (V111)
language: "python e typescript"       # As duas linguagens core do projeto
framework: "nextjs"                   # Arquitetura própria do Capacity Engine e painel Vanilla JS
package_manager: "npm"          # pip para o backend, npm se for empacotar/minificar o frontend
node_version: "20"                    # Estável para eventuais builds do frontend
python_version: "3.11"                # Ideal para processamento rápido e bibliotecas assíncronas do bot
author: "Dom"
git_remote: ""                        # Pode preencher com o link do seu repositório privado
```

---

## 🗂️ SEÇÃO 2 — ESTRUTURA DE PASTAS

**Execute:** Crie toda a estrutura abaixo com arquivos mínimos funcionais (nunca vazios).

```
{project_name}/
├── .claude/
│   ├── CLAUDE.md              # Memória do projeto para Claude Code
│   └── skills/                # Skills reutilizáveis (automações)
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── deploy.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── src/
│   ├── agents/                # Lógica dos agentes
│   ├── core/                  # Regras de negócio
│   ├── services/              # Integrações externas
│   ├── utils/                 # Helpers e utilitários
│   └── types/                 # Tipagens globais
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── agents-config.md
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
├── .env.example
├── .gitignore
├── .editorconfig
├── README.md
├── CHANGELOG.md
└── AGENTS.md                  # Este arquivo
```

---

## ⚙️ SEÇÃO 3 — CONFIGURAÇÃO DO AMBIENTE

### 3.1 — Git

```bash
git init
git checkout -b main
git config core.autocrlf false
git config core.eol lf
```

Se `git_remote` preenchido:
```bash
git remote add origin {git_remote}
```

### 3.2 — .gitignore

Gere `.gitignore` completo cobrindo:
- `node_modules/`, `dist/`, `build/`, `.next/`, `.turbo/`
- `__pycache__/`, `*.pyc`, `.venv/`, `venv/`
- `.env`, `.env.local`, `.env.*.local`
- `.DS_Store`, `Thumbs.db`
- `*.log`, `logs/`
- `.idea/`, `.vscode/` (exceto `settings.json` compartilhável)
- `coverage/`, `.nyc_output/`

### 3.3 — .editorconfig

```ini
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
trim_trailing_whitespace = false

[*.py]
indent_size = 4

[Makefile]
indent_style = tab
```

### 3.4 — .env.example

```env
# App
NODE_ENV=development
PORT=3000
APP_URL=http://localhost:3000

# Database
DATABASE_URL=

# Auth
JWT_SECRET=
JWT_EXPIRES_IN=7d

# AI / LLMs
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Crypto (se aplicável)
BINANCE_API_KEY=
BINANCE_SECRET=
BYBIT_API_KEY=
BYBIT_SECRET=
```

---

## 🧠 SEÇÃO 4 — CLAUDE.md (Memória Persistente do Projeto)

> O `CLAUDE.md` é carregado automaticamente toda vez que o Claude Code abre o projeto.
> É a "memória" do projeto — contexto que persiste entre sessões sem precisar reexplicar.
> Coloque em: `.claude/CLAUDE.md` (escopo de projeto) ou `~/.claude/CLAUDE.md` (global)

**Crie `.claude/CLAUDE.md` com o conteúdo abaixo (adapte ao projeto):**

```markdown
# {project_name} — Contexto do Projeto

## Visão geral
{project_description}

## Stack
- **Language:** {language}
- **Framework:** {framework}
- **Package Manager:** {package_manager}
- **Author:** {author}

## Comandos chave
- `npm run dev`        → Inicia desenvolvimento
- `npm run build`      → Build de produção
- `npm run test`       → Executa todos os testes
- `npm run test:unit`  → Apenas testes unitários
- `npm run lint`       → Verifica código
- `npm run type-check` → Checa tipos TypeScript

## Padrões do projeto
- TypeScript strict mode habilitado
- Commits seguem Conventional Commits (feat/fix/chore/docs/refactor)
- Testes obrigatórios para qualquer nova feature
- Nunca commitar `.env` — usar apenas `.env.example`
- PRs sempre passam pelo checklist de Dom-Security antes do merge

## Agentes disponíveis
Ver: docs/agents-config.md

## Contexto de negócio
- [Adicione aqui as regras de negócio importantes]
- [Decisões arquiteturais e o porquê foram tomadas]
- [Integrações externas ativas e suas particularidades]

## Estilo de código
- Componentes: PascalCase
- Funções/variáveis: camelCase
- Constantes globais: UPPER_SNAKE_CASE
- Arquivos: kebab-case
```

---

## 🤖 SEÇÃO 5 — AGENTES DE DESENVOLVIMENTO

### Hierarquia Multi-Agente

```
Dom-PM (Orquestrador — analisa, planeja e delega)
├── Dom-Architect     → Arquitetura, design patterns, decisões técnicas
├── Dom-Backend       → APIs, banco de dados, lógica server-side
├── Dom-Frontend      → UI/UX, componentes, estado, responsividade
├── Dom-DevOps        → CI/CD, Docker, infraestrutura, deploy
├── Dom-QA            → Testes, qualidade, code review, validação
└── Dom-Security      → Auditoria, OWASP, secrets, vulnerabilidades
```

**Crie `docs/agents-config.md`:**

```markdown
# Agentes de Desenvolvimento

## Como usar
Inicie sempre pelo Dom-PM. Ele analisa a task e delega para os especialistas.

Exemplo no Claude Code:
> "Dom-PM: preciso criar autenticação JWT"
> Dom-PM → Dom-Architect (design) → Dom-Backend (impl) → Dom-QA (testes) → Dom-Security (auditoria)

---

## Dom-PM — Orquestrador
**Prompt:**
"Você é Dom-PM. Analise a task a seguir, quebre em subtasks e delegue para os agentes corretos
na ordem certa. Defina o critério de conclusão de cada subtask. Task: {task}"

## Dom-Architect
**Prompt:**
"Você é Dom-Architect. Proponha a melhor arquitetura para {problema}, considerando
escalabilidade, manutenção e os padrões já usados no projeto (ver CLAUDE.md)."

## Dom-Backend
**Prompt:**
"Você é Dom-Backend especialista em {framework}. Implemente {feature} seguindo os padrões
do projeto. Inclua tratamento de erros e validação de input."

## Dom-Frontend
**Prompt:**
"Você é Dom-Frontend. Crie o componente {nome} com foco em UX, acessibilidade e performance.
Use os padrões de estilo definidos no projeto."

## Dom-DevOps
**Prompt:**
"Você é Dom-DevOps. Configure {pipeline/infra} para {dev/staging/prod}. Priorize
reprodutibilidade e zero-downtime deploy."

## Dom-QA
**Prompt:**
"Você é Dom-QA. Escreva testes completos para {módulo/função}. Cubra: happy path,
edge cases, erros esperados e casos limite."

## Dom-Security
**Prompt:**
"Você é Dom-Security. Audite {código/endpoint} com foco em OWASP Top 10. Identifique
vulnerabilidades, exposição de secrets e superfície de ataque."

---

## Fluxo padrão de uma feature

1. Dom-PM recebe a task e cria o plano
2. Dom-Architect valida a abordagem (se mudança estrutural)
3. Dom-Backend e/ou Dom-Frontend implementam
4. Dom-QA escreve/atualiza os testes
5. Dom-Security audita antes do merge
6. Dom-DevOps atualiza pipeline se necessário
```

---

## 🔄 SEÇÃO 6 — GITHUB ACTIONS (CI/CD)

### `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality:
    name: Lint, Type Check & Test
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Unit tests
        run: npm run test:unit -- --coverage

      - name: Integration tests
        run: npm run test:integration

      - name: Build
        run: npm run build

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: success()
```

### `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'production'
        type: choice
        options: [production, staging]

jobs:
  deploy:
    name: Deploy to ${{ github.event.inputs.environment || 'production' }}
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'production' }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install & Build
        run: |
          npm ci
          npm run build

      - name: Deploy
        run: |
          echo "Configure seu step de deploy aqui"
          # Vercel:  npx vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
          # Railway: railway up
          # VPS:     ssh user@server 'cd /app && git pull && npm ci && pm2 restart app'
```

### `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## 📋 O que foi feito?
> Descreva as mudanças de forma clara e objetiva.

## 🔗 Issue relacionada
Closes #

## 🧪 Tipo de mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Refatoração
- [ ] Documentação

## ✅ Checklist
- [ ] Código segue os padrões do projeto (ver .claude/CLAUDE.md)
- [ ] Testes adicionados/atualizados
- [ ] Build passando localmente
- [ ] Sem secrets ou dados sensíveis no código
- [ ] Dom-Security revisou (para mudanças em auth/dados críticos)

## 🤖 Agentes que trabalharam nessa PR
- [ ] Dom-Architect  - [ ] Dom-Backend  - [ ] Dom-Frontend
- [ ] Dom-DevOps     - [ ] Dom-QA       - [ ] Dom-Security
```

---

## 📦 SEÇÃO 7 — DEPENDÊNCIAS INICIAIS

### Node/TypeScript

```bash
# TypeScript
npm install -D typescript @types/node ts-node tsx

# Linting + formatação
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin prettier eslint-config-prettier

# Testes
npm install -D jest @types/jest ts-jest

# Utilitários essenciais
npm install dotenv zod

# Gerar configs base
npx tsc --init
```

### Python

Crie `requirements-dev.txt`:
```
pytest
pytest-asyncio
pytest-cov
black
flake8
mypy
python-dotenv
```

---

## 📝 SEÇÃO 8 — DOCUMENTAÇÃO BASE

### README.md

```markdown
# {project_name}

> {project_description}

## 🚀 Quick Start

\`\`\`bash
git clone {git_remote}
cd {project_name}
cp .env.example .env
# Edite .env com suas variáveis reais
npm install
npm run dev
\`\`\`

## 🤖 Agentes de desenvolvimento
Ver [docs/agents-config.md](docs/agents-config.md)

## 🧠 Memória do projeto (Claude Code)
Ver [.claude/CLAUDE.md](.claude/CLAUDE.md)

## 📜 Scripts

| Script | Descrição |
|--------|-----------|
| `npm run dev` | Desenvolvimento local |
| `npm run build` | Build produção |
| `npm run test` | Executa testes |
| `npm run lint` | Verifica código |

## 🔐 GitHub Secrets necessários
Configurar em Settings > Secrets and variables > Actions:
- Adicionar conforme variáveis do `.env.example`
```

### CHANGELOG.md

```markdown
# Changelog

## [Unreleased]

### Added
- Bootstrap inicial do projeto via AGENTS.md
- CLAUDE.md configurado (memória persistente para Claude Code)
- Hierarquia de agentes: Dom-PM, Architect, Backend, Frontend, DevOps, QA, Security
- GitHub Actions: CI (lint + test + build) e Deploy
- PR Template com checklist de agentes
```

---

## 🚀 SEÇÃO 9 — COMMIT INICIAL

```bash
git add .
git commit -m "chore: bootstrap inicial do projeto

- Estrutura de pastas e arquivos base criados
- .claude/CLAUDE.md configurado (memória persistente para Claude Code)
- Agentes de desenvolvimento documentados em docs/agents-config.md
- GitHub Actions configurados (ci.yml + deploy.yml)
- PR Template criado
- .env.example, .gitignore, .editorconfig configurados
- README.md e CHANGELOG.md gerados"
```

Se `git_remote` preenchido:
```bash
git push -u origin main
```

---

## ⚡ SEÇÃO 10 — REFERÊNCIA: SLASH COMMANDS (Claude Code)

> Cole no seu `CLAUDE.md` como referência rápida durante o desenvolvimento

| Comando | O que faz |
|---------|-----------|
| `/help` | Lista todos os comandos disponíveis |
| `/clear` | Reseta contexto (use entre tasks diferentes) |
| `/compact` | Comprime conversa para economizar tokens |
| `/model` | Troca entre Opus / Sonnet / Haiku |
| `/mcp` | Verifica conexões MCP ativas |
| `/doctor` | Diagnostica problemas de instalação |
| `/config` | Abre configurações |

**Referências de arquivo (digite `@` no Claude Code):**
- `@filename` → referencia arquivo específico
- `@folder/` → referencia pasta inteira
- `Tab` → autocomplete de caminhos

**Atalhos de teclado:**
- `Esc` → cancela execução
- `Esc Esc` → rewind de checkpoint
- `Ctrl+V` → cola imagem diretamente

**MCPs recomendados para conectar:**
```bash
# GitHub
claude mcp add --transport http github https://mcp.github.com

# Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# PostgreSQL (ajuste a connection string)
claude mcp add --transport http postgres https://mcp.supabase.com/mcp
```

---

## 🔧 SEÇÃO 11 — TÉCNICAS DE PROMPT (para uso com os agentes)

| Técnica | Quando usar | Exemplo |
|---------|-------------|---------|
| **Seja específico** | Sempre | "Crie endpoint POST /auth/login com JWT, validação Zod, retorno 200/401" |
| **Dê exemplos** | Output tem formato definido | "Retorne no formato: `{ token, expiresIn, user: {id, email} }`" |
| **Chain of thought** | Tasks complexas | "Primeiro analise, depois planeje, então implemente" |
| **Defina constraints** | Controle de qualidade | "Máximo 50 linhas por função. Sem any no TypeScript." |
| **Assign roles** | Expertise específica | "Você é Dom-Security especialista em OWASP" |
| **Use /clear** | Entre tasks não relacionadas | Reseta contexto poluído |

---

## ✅ SEÇÃO 12 — CHECKLIST DE CONCLUSÃO

- [ ] Estrutura de pastas criada
- [ ] `.claude/CLAUDE.md` criado com contexto do projeto
- [ ] `.gitignore` gerado
- [ ] `.editorconfig` criado
- [ ] `.env.example` com variáveis base
- [ ] Git inicializado com branch `main`
- [ ] Remote configurado (se fornecido)
- [ ] GitHub Actions: `ci.yml` e `deploy.yml` criados
- [ ] PR Template criado
- [ ] `docs/agents-config.md` com hierarquia de agentes
- [ ] `README.md` gerado
- [ ] `CHANGELOG.md` criado
- [ ] Dependências instaladas (se aplicável)
- [ ] Commit inicial realizado

---

## 📊 SEÇÃO 13 — RELATÓRIO FINAL

```
╔══════════════════════════════════════════════════╗
║     ✅ BOOTSTRAP CONCLUÍDO — {project_name}      ║
╠══════════════════════════════════════════════════╣
║  📁 Pastas criadas:          X                   ║
║  📄 Arquivos gerados:        X                   ║
║  📦 Dependências:            X pacotes           ║
║  🤖 Agentes configurados:    7                   ║
║  🔄 GitHub Actions:          2 workflows         ║
║  🧠 CLAUDE.md:               ✅ configurado      ║
║  🌿 Branch ativa:            main                ║
║  🔗 Remote:                  {git_remote}        ║
╠══════════════════════════════════════════════════╣
║  ⚡ PRÓXIMOS PASSOS:                             ║
║                                                  ║
║  1. Edite .env com suas variáveis reais          ║
║  2. Revise .claude/CLAUDE.md                     ║
║  3. Configure GitHub Secrets                     ║
║  4. Conecte MCPs: claude mcp add ...             ║
║  5. npm run dev → pode começar!                  ║
╚══════════════════════════════════════════════════╝
```

---

> **Versão:** 2.0.0  
> **Criado por:** Dom — OpenClaw Agent System  
> **Compatível com:** Claude Code CLI · Claude.ai · OpenClaw  
> **Docs:** [code.claude.com/docs](https://code.claude.com/docs/en/setup) · [MCP Servers](https://anthropic.com/mcp)
