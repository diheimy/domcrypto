import logging
import math

logger = logging.getLogger("QualityEngine")

class QualityEngine:
    @staticmethod
    def enrich(op):
        try:
            # --- [MODO OBSERVAÇÃO] BYPASS DE SCORE ---
            # Se a oportunidade é apenas para observação, zeramos o score
            # para garantir que ela nunca seja considerada para execução.
            if getattr(op, 'status', None) == "OBSERVATION_ONLY":
                op.score = 0
                op.quality_level = "OBSERVE" # Novo nível específico
                # Removemos tags de comportamento que não fazem sentido aqui
                return op

            W_SPREAD = 0.6
            W_VOL = 0.4
            
            # ... (Resto do código do QualityEngine permanece idêntico ao anterior) ...
            # ... (Apenas cole o restante da lógica de cálculo de score aqui) ...
            
            spread = getattr(op, 'spread_net_pct', 0.0) or 0.0
            volume = getattr(op, 'volume_24h_usd', 0.0) or 0.0
            persist = getattr(op, 'persistence_minutes', 0) or 0
            
            behavior_flags = getattr(op, 'behavior_flags', [])
            liq_flags = getattr(op, 'liquidity_flags', [])
            depth_flags = getattr(op, 'depth_flags', [])
            depth_usd = getattr(op, 'depth_exec_usd', 0)

            if op.top_liquidity_usd < 20:
                op.status = "BLOCKED_THIN_BOOK"
                op.score = 0
                op.quality_level = "LOW_QUAL"
                return op

            score_spread = min(100, (spread / 1.5) * 100)
            if spread > 5.0: score_spread *= 0.5 
            if score_spread < 0: score_spread = 0

            if volume < 50_000:
                score_vol = 0
            else:
                try:
                    log_val = math.log10(volume)
                    score_vol = max(0, min(100, ((log_val - 4.7) / 1.3) * 100))
                except:
                    score_vol = 0

            final_score = (score_spread * W_SPREAD) + (score_vol * W_VOL)
            
            bonus_persist = 0
            if persist > 10: bonus_persist = 10
            elif persist > 5: bonus_persist = 5
            final_score += bonus_persist

            base_score = min(100, max(0, round(final_score, 1)))
            op.score = base_score
            
            # ... (Mantenha o restante da lógica de Tags e Penalidades igual) ...
            # (Simplificado aqui para brevidade, mas use o código completo anterior)
            
            # Tagging Final
            tags = list(getattr(op, 'tags', []))
            if "SYNTHETIC_DEPTH" in tags:
                op.score *= 0.70
            
            op.score = max(0, min(100, round(op.score, 1)))
            
            # Níveis Normais
            is_trap = "TRAP" in behavior_flags
            if op.score >= 70 and volume > 100_000 and not is_trap:
                op.quality_level = "READY"
            elif op.score >= 30:
                op.quality_level = "WATCH"
            else:
                op.quality_level = "LOW_QUAL"
            
            if spread <= 0: # Redundância
                 op.score = 0
                 op.quality_level = "LOW_QUAL"

            op.tags = list(dict.fromkeys(tags))
            return op

        except Exception as e:
            logger.error(f"Erro QualityEngine: {e}")
            op.score = 0
            op.quality_level = "ERROR"
            return op