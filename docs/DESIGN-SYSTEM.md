# DomCrypto — Design System
**Versão:** 2.0
**Atualizado:** 2026-03-09
**Framework:** UI/UX Pro Max (Real-Time Monitoring + Dark Mode OLED)

---

## 🎯 Visão Geral

**Tipo de Produto:** Dashboard de Arbitragem Crypto
**Categoria:** Real-Time Monitoring / Financial Dashboard
**Público:** Traders, operadores de arbitragem, analistas

---

## 🎨 Cores

### Palette Principal

| Variável | Valor | Uso |
|----------|-------|-----|
| `--bg-primary` | `#0F172A` | Fundo principal (slate-900) |
| `--bg-secondary` | `#1E293B` | Superfícies secundárias (slate-800) |
| `--bg-surface` | `rgba(30, 41, 59, 0.7)` | Cards com glassmorphism |
| `--text-primary` | `#F8FAFC` | Texto principal (slate-50) |
| `--text-secondary` | `#94A3B8` | Texto secundário (slate-400) |
| `--text-muted` | `#64748B` | Texto desativado/muted (slate-500) |

### Cores de Marca

| Variável | Valor | Uso |
|----------|-------|-----|
| `--primary` | `#F59E0B` | **Gold** — Cor primária (confiança, valor) |
| `--primary-light` | `#FBBF24` | Highlight, hover states |
| `--primary-glow` | `rgba(245, 158, 11, 0.4)` | Glow effects |

### Cores de Status

| Status | Cor | Hex | Uso |
|--------|-----|-----|-----|
| **Success/Positive** | Green | `#10B981` | Spread positivo, ativo, online |
| **Danger/Negative** | Red | `#EF4444` | Spread negativo, killed, erro |
| **Info/Ready** | Blue | `#3B82F6` | Ready status, futures |
| **Warning** | Amber | `#F59E0B` | Atenção, pending |

### Gradientes

```css
--gradient-gold: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);
--gradient-green: linear-gradient(135deg, #10B981 0%, #34D399 100%);
--gradient-red: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
--gradient-header: linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.1), transparent);
```

---

## 🔤 Tipografia

### Fontes (Google Fonts)

```css
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Exo+2:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700;800&family=Roboto+Mono:wght@400;500;700&display=swap');
```

### Hierarquia Tipográfica

| Elemento | Fonte | Tamanho | Peso | Uso |
|----------|-------|---------|------|-----|
| **H1 / Logo** | Orbitron | 24-32px | 700-800 | Títulos principais, logo |
| **H2 / Section** | Orbitron | 18-24px | 600-700 | Seções, headers |
| **Body** | Exo 2 | 14-16px | 400-500 | Texto corrido, labels |
| **Dados/Números** | JetBrains Mono | 12-14px | 600-700 | Preços, volumes, spreads |
| **Capacidade/Tags** | Roboto Mono | 10-12px | 500-700 | Dados técnicos, capacity |

### Line-height

```css
--line-height-heading: 1.2;    /* Orbitron */
--line-height-body: 1.5;       /* Exo 2 */
--line-height-data: 1.4;       /* JetBrains Mono */
```

---

## 🎭 Estilo Visual

### Categoria: **Dark Mode OLED + Real-Time Monitoring**

**Keywords:** Dark theme, high contrast, low light, eye-friendly, power efficient, live data

**Características:**
- ✅ Fundo preto profundo (#0F172A)
- ✅ Alto contraste (WCAG AAA)
- ✅ Glow effects sutis em elementos ativos
- ✅ Glassmorphism com backdrop-blur
- ✅ Bordas sutis para definição

### Efeitos

```css
/* Glassmorphism */
--glass-blur: blur(16px);
--glass-border: rgba(148, 163, 184, 0.1);
--glass-border-hover: rgba(245, 158, 11, 0.3);

/* Shadows */
--shadow-modern: 0 4px 24px rgba(0, 0, 0, 0.5);
--shadow-glow: 0 0 20px rgba(245, 158, 11, 0.4);
--shadow-green: 0 0 20px rgba(16, 185, 129, 0.4);
--shadow-red: 0 0 20px rgba(239, 68, 68, 0.4);

/* Transitions */
--transition-smooth: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
--transition-bounce: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
```

### Animações

```css
/* Live indicator pulse */
@keyframes pulse-live {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); box-shadow: 0 0 8px var(--green-glow); }
}

/* Loading spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 📐 Layout

### Grid System

```css
--grid-gap: 8px;
--card-padding: 12px;
--sidebar-width: 256px;   /* 64 */
--header-height: 56px;
```

### Breakpoints

| Nome | Tamanho | Uso |
|------|---------|-----|
| Mobile | 375px | Mínimo suportado |
| Tablet | 768px | Filtros 2 colunas |
| Desktop | 1024px | Sidebar visível |
| Large | 1440px | Layout completo |

### Z-Index Scale

```css
--z-sidebar: 40;
--z-overlay: 50;
--z-modal: 100;
--z-toast: 1000;
```

---

## 🧩 Componentes

### Sidebar
- **Largura:** 256px (64)
- **Background:** `--bg-surface`
- **Border:** `--border-gold`
- **Z-index:** 40
- **Estado ativo:** `bg-gold-glow border-l-[3px] border-gold`

### Toolbar
- **Padding:** 16px
- **Border-radius:** 12px
- **Live indicator:** Pulse animation (2s infinite)

### Tabela de Oportunidades
- **Row height:** 52px (padding 10px)
- **Header background:** `rgba(15, 23, 42, 0.4)`
- **Hover:** `rgba(245, 158, 11, 0.04)`
- **Sort ativo:** `rgba(245, 158, 11, 0.12)`

### Score Badges
- **Ready:** Green glow, `--shadow-green`
- **Watch:** Amber glow, `--shadow-glow`
- **Low quality:** Muted, opacity 0.7

### Action Buttons
- **Tamanho:** 26x26px
- **View:** Blue (`rgba(59, 130, 246, 0.15)`)
- **Execute:** Green (`rgba(16, 185, 129, 0.15)`)
- **Kill:** Red (`rgba(239, 68, 68, 0.15)`)
- **Hover:** Scale 1.15, opacity aumenta

---

## ♿ Acessibilidade (Priority 1 - CRITICAL)

### Requisitos Obrigatórios

| Regra | Implementação |
|-------|---------------|
| **Color Contrast** | 4.5:1 mínimo (WCAG AA) |
| **Focus States** | `outline: 2px solid var(--primary)` |
| **Keyboard Nav** | Tab order lógico, `Escape` fecha modais |
| **ARIA Labels** | Todos botões icônicos |
| **Reduced Motion** | `@media (prefers-reduced-motion)` |
| **No Emoji Icons** | SVG apenas (Lucide) |

### Keyboard Shortcuts

| Atalho | Ação |
|--------|------|
| `Ctrl/Cmd + K` | Focar search |
| `Ctrl/Cmd + F` | Abrir filtros |
| `Escape` | Fechar filtros |

---

## 📊 Ícones

**Biblioteca:** Lucide React (consistente, 24x24px)

| Ícone | Uso | Tamanho |
|-------|-----|---------|
| `Eye` | Ver detalhes | 14px |
| `Play` | Executar | 14px |
| `X` | Descartar | 14px |
| `Filter` | Filtros | 14px |
| `Settings` | Configurações | 14px |
| `Search` | Busca | 14px |
| `Pause/Play` | Pausar/Retomar | 14px |

---

## ✅ Pre-Delivery Checklist

### Visual Quality
- [ ] No emojis as icons (use SVG: Lucide)
- [ ] All icons from consistent icon set
- [ ] Hover states don't cause layout shift
- [ ] Use theme colors directly

### Interaction
- [ ] All clickable elements have `cursor-pointer`
- [ ] Hover states provide clear visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states visible for keyboard navigation

### Light/Dark Mode
- [ ] Dark mode text has sufficient contrast (4.5:1)
- [ ] Glass/transparent elements visible
- [ ] Borders visible in both modes

### Layout
- [ ] No content hidden behind fixed sidebars
- [ ] Responsive at 375px, 768px, 1024px, 1440px
- [ ] No horizontal scroll on mobile

### Accessibility
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only indicator
- [ ] `prefers-reduced-motion` respected

---

## 🚀 Anti-Patterns (EVITAR)

| Pattern | Problema | Solução |
|---------|----------|---------|
| Slow updates + No automation | Dados desatualizados | Auto-refresh 5-10s |
| Emojis como ícones | Amador, inconsistente | SVG (Lucide) |
| Remover focus outline | Inacessível | Usar `focus:ring` |
| Animações infinitas decorativas | Distrativo | Apenas loading indicators |
| Tabelas wide sem scroll | Quebra layout | `overflow-x: auto` |

---

## 📚 Referências

- **UI/UX Pro Max:** Real-Time Monitoring Dashboard
- **Dark Mode OLED:** Baixo consumo, alto contraste
- **Tailwind CSS Colors:** Slate + Amber palette
- **Lucide Icons:** SVG consistente e acessível
- **Google Fonts:** Orbitron, Exo 2, JetBrains Mono

---

## 🔧 Tailwind Config

```js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        display: ['Orbitron', 'sans-serif'],
        body: ['Exo 2', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        data: ['Roboto Mono', 'monospace'],
      },
      colors: {
        primary: '#F59E0B',
        'primary-light': '#FBBF24',
        green: '#10B981',
        red: '#EF4444',
        blue: '#3B82F6',
      },
    },
  },
}
```
