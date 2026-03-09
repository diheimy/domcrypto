import logging

logger = logging.getLogger("PartialRebalance")

class PartialRebalanceEngine:
    """
    F17 — Partial Exit & Auto-Rebalance Engine (Institutional MVP)

    Ajusta posições abertas de forma progressiva:
    - Reduções parciais por Regime ou Trust
    - Lock de lucro (Profit Taking parcial)
    - Rebalanceamento defensivo

    Hierarquia: F11 -> F12 -> F17 -> F15 -> F16
    """
    
    @staticmethod
    def evaluate(op):
        try:
            # Em um pipeline de entrada, 'current_position_usd' seria o valor executado agora.
            # Em um loop de monitoramento, seria o saldo atual da posição.
            # Usamos getattr com fallback seguro.
            current_pos = getattr(op, "current_position_usd", 0.0)
            
            # Se não há posição (ou acabou de ser preenchida como 0), não há o que rebalancear
            # Mas permitimos avaliar se filled_usd > 0 (acabou de entrar)
            if current_pos <= 0:
                filled = getattr(op, "filled_usd", 0.0)
                if filled > 0:
                    current_pos = filled
                else:
                    return op

            plan = {
                "action": "HOLD",
                "reduce_pct": 0.0,
                "reason": [],
                "confidence": 0.6
            }

            regime = getattr(op, "market_regime", "NORMAL")
            trust = getattr(op, "trust_score", 50)
            exec_quality = getattr(op, "execution_quality_score", 100)
            pnl = getattr(op, "pnl_pct", 0.0)
            holding = getattr(op, "holding_hours", 0)

            # --- 1. Regime-Based Reduction (Ajuste Macro) ---
            if regime == "VOLATILE":
                plan["reduce_pct"] = max(plan["reduce_pct"], 0.25)
                plan["reason"].append("REGIME_VOLATILE")
            elif regime == "STRESSED":
                plan["reduce_pct"] = max(plan["reduce_pct"], 0.50)
                plan["reason"].append("REGIME_STRESSED")

            # --- 2. Trust Degradation (Ajuste de Confiança) ---
            if 40 <= trust < 50:
                plan["reduce_pct"] = max(plan["reduce_pct"], 0.20)
                plan["reason"].append("TRUST_WEAKENING")
            elif 30 <= trust < 40:
                plan["reduce_pct"] = max(plan["reduce_pct"], 0.35)
                plan["reason"].append("TRUST_LOW")

            # --- 3. Profit Lock (Realização Parcial) ---
            # Regra: Se lucrou > 10% e segurou por > 6h, bota 30% no bolso.
            if pnl >= 0.10 and holding >= 6:
                plan["reduce_pct"] = max(plan["reduce_pct"], 0.30)
                plan["reason"].append("PROFIT_LOCK")

            # --- 4. Execution Degradation (Ajuste Técnico) ---
            if exec_quality < 60:
                plan["reduce_pct"] = max(plan["reduce_pct"], 0.25)
                plan["reason"].append("EXECUTION_DEGRADING")

            # --- Clamp e Validação ---
            if plan["reduce_pct"] > 0:
                # Regra de Ouro: Nunca reduzir abaixo de 10% da posição original via F17
                # (Se precisar sair tudo, o F15 que decide)
                max_reducible = 0.90
                plan["reduce_pct"] = min(plan["reduce_pct"], max_reducible)

                plan["action"] = "PARTIAL_REDUCE"
                plan["confidence"] = 0.75

            # Persistência
            # Só grava se houver ação, para não poluir o objeto
            if plan["action"] != "HOLD":
                plan["reason"] = list(set(plan["reason"]))
                op.partial_rebalance_plan = plan
            else:
                op.partial_rebalance_plan = None

            return op

        except Exception as e:
            logger.error(f"Erro no PartialRebalanceEngine: {e}")
            return op