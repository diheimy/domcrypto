# dom-crypto — Contexto do Projeto

## Visão geral
Bot fullstack de arbitragem de criptomoedas (Spot/Futuros)

## Stack
- **Language:** Python e TypeScript
- **Framework:** Next.js
- **Package Manager:** npm
- **Author:** Dom

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
- Bot de arbitragem de criptomoedas operando em Spot e Futuros
- Integração com exchanges: Binance, Bybit
- Processamento assíncrono para baixa latência

## Estilo de código
- Componentes: PascalCase
- Funções/variáveis: camelCase
- Constantes globais: UPPER_SNAKE_CASE
- Arquivos: kebab-case
