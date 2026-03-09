import logging

logger = logging.getLogger("TrustEngine")

class TrustEngine:
    """
    F12 — Trust Engine (Institutional MVP)
    Calcula score de confiança (0-100) baseado em métricas reais de execução (F11).
    """

    @staticmethod
    def compute(exchange, symbol, executions: list):
        if not executions:
            return 50  # Neutro conservador (nem ama, nem odeia)

        total = len(executions)
        fails = 0
        slippage_sum = 0
        fill_sum = 0
        quality_sum = 0

        for ex in executions:
            quality_sum += ex.get("execution_quality_score", 0)
            fill_sum += ex.get("fill_ratio", 0)
            slippage_sum += abs(ex.get("slippage_pct", 0))

            status = ex.get("execution_status")
            if status != "FILLED":
                fails += 1

        # Médias
        avg_quality = quality_sum / total
        avg_fill = fill_sum / total
        avg_slippage = slippage_sum / total
        failure_rate = fails / total

        # Scores Derivados
        # Slippage Score: 0.4% de slippage médio zera este componente (100 - 0.4*250 = 0)
        slippage_score = max(0, 100 - avg_slippage * 250)
        
        # Reliability Score: Taxa de falha pura
        reliability_score = 100 - failure_rate * 100

        # Fórmula Institucional Ponderada
        # 40% Qualidade Geral | 25% Fill Ratio | 20% Slippage | 15% Confiabilidade
        trust = (
            0.40 * avg_quality +
            0.25 * avg_fill * 100 +
            0.20 * slippage_score +
            0.15 * reliability_score
        )

        return int(max(0, min(trust, 100)))