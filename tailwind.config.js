module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/frontend/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#000000',
        surface: '#060607',
        card: '#0f1319',
        hover: '#151a23',
        border: 'rgba(255,255,255,0.06)',
        'border-gold': 'rgba(252,213,53,0.25)',
        gold: '#FCD535',
        'gold-dim': '#f0b90b',
        'gold-glow': 'rgba(252,213,53,0.15)',
        green: '#0ecb81',
        red: '#f6465d',
        blue: '#3b82f6',
        muted: '#848e9c',
      },
      fontFamily: {
        ui: ['Geist Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
