module.exports = {
  content: [
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/frontend/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        surface: 'var(--surface)',
        card: 'var(--card)',
        hover: 'var(--hover)',
        border: 'var(--border)',
        'border-gold': 'var(--border-gold)',
        gold: 'var(--gold)',
        'gold-dim': 'var(--gold-dim)',
        'gold-glow': 'var(--gold-glow)',
        green: 'var(--green)',
        'green-glow': 'var(--green-glow)',
        red: 'var(--red)',
        'red-glow': 'var(--red-glow)',
        blue: 'var(--blue)',
        'blue-glow': 'var(--blue-glow)',
        muted: 'var(--muted)',
        primary: 'var(--primary)',
        'primary-light': 'var(--primary-light)',
        'primary-glow': 'var(--primary-glow)',
      },
      fontFamily: {
        display: ['Orbitron', 'sans-serif'],
        body: ['Exo 2', 'sans-serif'],
        data: ['Roboto Mono', 'monospace'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        glow: 'var(--shadow-glow)',
        green: 'var(--shadow-green)',
        red: 'var(--shadow-red)',
        blue: 'var(--shadow-blue)',
      },
      spacing: {
        'sidebar': 'var(--sidebar-width)',
      },
    },
  },
  plugins: [],
}
