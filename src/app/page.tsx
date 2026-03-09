export default function HomePage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gradient-gold mb-2">DomCrypto</h1>
        <p className="text-muted">Bot de Arbitragem Spot x Futuros</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <a
          href="/dashboard"
          className="glass rounded-xl p-6 border border-border hover:border-gold transition-all hover:shadow-glow group"
        >
          <h2 className="text-xl font-semibold text-white mb-2 group-hover:text-gold transition-colors">Dashboard</h2>
          <p className="text-muted">Visão geral do sistema com KPIs em tempo real</p>
        </a>

        <a
          href="/spot-futuros"
          className="glass rounded-xl p-6 border border-border hover:border-gold transition-all hover:shadow-glow group"
        >
          <h2 className="text-xl font-semibold text-white mb-2 group-hover:text-gold transition-colors">Spot x Futuros</h2>
          <p className="text-muted">Tabela completa de oportunidades de arbitragem</p>
        </a>

        <a
          href="/historico"
          className="glass rounded-xl p-6 border border-border hover:border-gold transition-all hover:shadow-glow group"
        >
          <h2 className="text-xl font-semibold text-white mb-2 group-hover:text-gold transition-colors">Histórico</h2>
          <p className="text-muted">Registro de operações e análise de PnL</p>
        </a>

        <a
          href="/configuracoes"
          className="glass rounded-xl p-6 border border-border hover:border-gold transition-all hover:shadow-glow group"
        >
          <h2 className="text-xl font-semibold text-white mb-2 group-hover:text-gold transition-colors">Configurações</h2>
          <p className="text-muted">Ajuste os parâmetros do sistema</p>
        </a>
      </div>
    </div>
  )
}
