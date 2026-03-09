import logging

logger = logging.getLogger("MarketRegime")

class MarketRegimeEngine:
    """
    F14 — Market Regime Engine (Institutional MVP)
    Classifica o regime de mercado (CALM, NORMAL, VOLATILE, STRESSED)
    e gera fatores de ajuste para Score, Capital e Execução.
    """
    
    @staticmethod
    def detect(op):
        try:
            volatility_score = 0

            # --- 1. Spread Instável (Behavior F4) ---
            # Se o desvio padrão do spread é alto, indica incerteza
            spread_std = getattr(op, "spread_std_pct", 0.0)
            if spread_std > 0.25:
                volatility_score += 2
            elif spread_std > 0.15:
                volatility_score += 1

            # --- 2. Slippage Real Recente (F11) ---
            # Se estamos tomando slippage, o mercado está rápido ou raso
            slippage = abs(getattr(op, "slippage_pct", 0.0))
            if slippage > 0.30:
                volatility_score += 2
            elif slippage > 0.15:
                volatility_score += 1

            # --- 3. Liquidez do Topo ---
            # Pouca liquidez = Maior volatilidade potencial
            liquidity = getattr(op, "top_liquidity_usd", 0.0)
            if liquidity < 25_000:
                volatility_score += 2
            elif liquidity < 75_000:
                volatility_score += 1

            # --- 4. Funding Extremo (F8.2) ---
            # Funding alto indica desbalanço forte (FOMO ou FUD)
            funding = abs(getattr(op, "funding_rate_pct", 0.0))
            if funding > 0.15:
                volatility_score += 1

            # --- Classificação de Regime ---
            if volatility_score >= 5:
                regime = "STRESSED"
            elif volatility_score >= 3:
                regime = "VOLATILE"
            elif volatility_score >= 1:
                regime = "NORMAL"
            else:
                regime = "CALM"

            # --- Definição de Fatores Institucionais ---
            if regime == "CALM":
                factors = {
                    "score_factor": 1.05,        # Bônus leve
                    "allocation_factor": 1.00,   # Alocação cheia
                    "aggressiveness_cap": "AGGRESSIVE" # Liberado
                }
            elif regime == "NORMAL":
                factors = {
                    "score_factor": 1.00,
                    "allocation_factor": 1.00,
                    "aggressiveness_cap": "BALANCED" # Teto Balanceado
                }
            elif regime == "VOLATILE":
                factors = {
                    "score_factor": 0.90,        # Penaliza score
                    "allocation_factor": 0.70,   # Reduz mão em 30%
                    "aggressiveness_cap": "PASSIVE" # Força Passivo
                }
            else:  # STRESSED
                factors = {
                    "score_factor": 0.75,        # Penaliza forte
                    "allocation_factor": 0.40,   # Reduz mão em 60%
                    "aggressiveness_cap": "PASSIVE" # Força Passivo
                }

            # Persistência
            op.market_regime = regime
            op.market_regime_factors = factors

            return op

        except Exception as e:
            logger.error(f"Erro no MarketRegimeEngine: {e}")
            return op