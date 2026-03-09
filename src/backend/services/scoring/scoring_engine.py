import logging

logger = logging.getLogger("ScoringEngine")

class ScoringEngine:
    """
    F13 — Scoring Engine Institucional
    Calcula um score unificado (0-100) para a qualidade da oportunidade.
    O Score serve de input para dimensionamento de lote e decisão, mas não bloqueia sozinho.
    """
    
    # Pesos por Perfil de Risco
    PROFILES = {
        "conservative": {"spread": 0.3, "liquidity": 0.4, "trust": 0.3},
        "balanced":     {"spread": 0.5, "liquidity": 0.3, "trust": 0.2},
        "aggressive":   {"spread": 0.7, "liquidity": 0.2, "trust": 0.1}
    }

    @staticmethod
    def calculate(op, profile="balanced"):
        try:
            # Seleciona pesos (default: balanced)
            weights = ScoringEngine.PROFILES.get(profile, ScoringEngine.PROFILES["balanced"])
            
            # --- 1. Componente Spread (0-100) ---
            # Meta: 1.0% de spread líquido = 100 pontos
            # Spreads maiores que 1% saturam em 100 (excelência máxima)
            spread_val = getattr(op, "spread_net_pct", 0.0)
            score_spread = min(max(spread_val * 100.0, 0.0), 100.0)
            
            # --- 2. Componente Liquidez (0-100) ---
            # Meta: $50k USD no topo = 100 pontos
            # Permite escala linear para volumes menores
            liq_val = getattr(op, "top_liquidity_usd", 0.0)
            score_liq = min(max((liq_val / 50000.0) * 100.0, 0.0), 100.0)
            
            # --- 3. Componente Confiança (0-100) ---
            # Trust score já vem normalizado (50 é neutro)
            score_trust = float(getattr(op, "trust_score", 50))
            
            # --- 4. Cálculo Ponderado Base ---
            raw_score = (
                (score_spread * weights["spread"]) +
                (score_liq * weights["liquidity"]) +
                (score_trust * weights["trust"])
            )
            
            # --- 5. Ajustes e Penalizações (Fatores Multiplicativos) ---
            # Penaliza score baseando-se em riscos laterais, mas nunca zera arbitrariamente
            adjustment_factor = 1.0
            
            # A. Custo de Funding Alto?
            funding_cost = getattr(op, "funding_cost_pct", 0.0)
            if funding_cost > 0.05: # Pagando mais que 0.05% por 8h
                adjustment_factor *= 0.85
            
            # B. Regime de Mercado?
            regime = getattr(op, "market_regime", "NORMAL")
            if regime == "STRESSED":
                adjustment_factor *= 0.70 # Reduz 30% do score em stress
            elif regime == "HIGH_VOLATILITY":
                adjustment_factor *= 0.90

            # C. Símbolo Novo/Desconhecido?
            if getattr(op, "spread_seen_count", 100) < 5:
                adjustment_factor *= 0.80

            # --- 6. Score Final ---
            final_score = raw_score * adjustment_factor
            
            # [CORREÇÃO] Clamp Rigoroso (0-100)
            # Garante que penalizações ou bugs matemáticos nunca gerem score < 0
            final_score = max(0.0, min(100.0, final_score))
            
            # --- 7. Persistência ---
            op.score = final_score
            
            # Auditoria detalhada
            op.score_breakdown = {
                "base_spread": round(score_spread, 1),
                "base_liq": round(score_liq, 1),
                "base_trust": round(score_trust, 1),
                "adj_factor": round(adjustment_factor, 2),
                "profile": profile
            }
            
            # Opcional: Define qualidade textual para frontend
            if final_score >= 80: op.quality_level = "READY"
            elif final_score >= 50: op.quality_level = "WATCH"
            else: op.quality_level = "WEAK"

            return op

        except Exception as e:
            logger.error(f"Erro no ScoringEngine: {e}")
            # Em caso de erro, define score neutro/baixo para não bloquear nem executar cegamente
            op.score = 0.0 
            op.quality_level = "ERROR"
            return op