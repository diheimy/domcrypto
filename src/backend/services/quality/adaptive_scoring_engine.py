import logging

logger = logging.getLogger("AdaptiveScoring")

class AdaptiveScoringEngine:
    """
    F13 — Adaptive Scoring Engine (Institutional MVP)
    Ajusta o score base com base em Trust (Histórico) e Execução (Recente).
    Transforma o Score Teórico (F1-F5) em Score Operacional.
    """
    
    @staticmethod
    def apply(op, trust_score: int):
        try:
            base_score = getattr(op, "score", 0)
            
            # Se o score base já for zero ou negativo, não há o que adaptar
            if base_score <= 0:
                return op

            # --- 1. Fator de Confiança (Trust) ---
            # Regra de Faixas Institucional (Step Function)
            if trust_score >= 80:
                trust_factor = 1.10  # Bônus de confiança (+10%)
            elif trust_score >= 60:
                trust_factor = 1.05  # Leve bônus (+5%)
            elif trust_score >= 40:
                trust_factor = 1.00  # Neutro
            elif trust_score >= 30:
                trust_factor = 0.90  # Penalidade leve (-10%)
            else:
                trust_factor = 0.75  # Penalidade severa (-25%)

            # --- 2. Penalidade por execução ruim IMEDIATA ---
            # Caso o objeto OP já tenha dados de execução recente (ex: retries ou re-scoring)
            exec_quality = getattr(op, "execution_quality_score", None)

            exec_factor = 1.0
            if exec_quality is not None:
                if exec_quality < 50:
                    exec_factor = 0.85
                elif exec_quality < 70:
                    exec_factor = 0.95

            # --- 3. Score Final ---
            adaptive_score = base_score * trust_factor * exec_factor

            # Clamp institucional (0 a 100)
            adaptive_score = max(0, min(int(adaptive_score), 100))

            # --- Persistência (Rastreabilidade) ---
            op.score_base = base_score           # Score original (F1-F5)
            op.score_adaptive = adaptive_score   # Score ajustado (F13)
            
            # O sistema passa a usar o score adaptativo como "A Verdade"
            op.score = adaptive_score
            
            op.trust_score = trust_score
            op.score_adjustment_factor = round(trust_factor * exec_factor, 3)

            return op

        except Exception as e:
            logger.error(f"Erro no AdaptiveScoringEngine: {e}")
            return op