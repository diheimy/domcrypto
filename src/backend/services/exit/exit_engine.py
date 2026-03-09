import logging

logger = logging.getLogger("ExitEngine")

class ExitEngine:
    """
    F15 — Regime-Aware Exit & Kill Engine (Institutional MVP)
    Decide quando e como sair de posições abertas baseando-se em Regime, Trust e Execução.
    Garante hierarquia de severidade: KILL > HARD > SOFT > HOLD.
    """
    
    @staticmethod
    def decide(op):
        try:
            # Plano Base (Default)
            plan = {
                "action": "HOLD",
                "urgency": "LOW",
                "recommended_order_type": "LIMIT",
                "reason": [],
                "confidence": 0.5
            }

            # Extração Segura de Dados
            regime = getattr(op, "market_regime", "NORMAL")
            exec_quality = getattr(op, "execution_quality_score", 100)
            slippage = abs(getattr(op, "slippage_pct", 0.0))
            trust = getattr(op, "trust_score", 50)
            funding = getattr(op, "funding_cost_pct", 0.0)
            holding = getattr(op, "holding_hours", 0) # Em um pipeline real-time, isso viria do PortfolioState
            pnl = getattr(op, "pnl_pct", 0.0)

            # --- 1. KILL CONDITIONS (Prioridade Máxima - Retorna Imediatamente) ---
            # Falha catastrófica de execução ou slippage extremo
            if slippage > 1.0:
                plan.update({
                    "action": "KILL",
                    "urgency": "IMMEDIATE",
                    "recommended_order_type": "MARKET",
                    "confidence": 0.95
                })
                plan["reason"].append(f"EXTREME_SLIPPAGE_{slippage:.2f}%")
                return ExitEngine._finalize(op, plan)

            # Para as demais condições, usamos variáveis locais para definir a severidade máxima
            action_severity = 0 # 0=HOLD, 1=SOFT, 2=HARD
            current_action = "HOLD"
            
            # --- 2. REGIME CHECK ---
            if regime == "STRESSED":
                action_severity = max(action_severity, 2)
                plan["reason"].append("MARKET_STRESSED")
            elif regime == "VOLATILE":
                action_severity = max(action_severity, 1)
                plan["reason"].append("MARKET_VOLATILE")

            # --- 3. EXECUTION QUALITY & TRUST CHECK ---
            if exec_quality < 40:
                action_severity = max(action_severity, 2)
                plan["reason"].append(f"LOW_EXEC_QUALITY_{exec_quality}")
            
            if trust < 30:
                action_severity = max(action_severity, 2)
                plan["reason"].append(f"TRUST_COLLAPSE_{trust}")

            # --- 4. FUNDING & TIME CHECK (Apenas Soft) ---
            if funding > 0.10 and holding > 8:
                action_severity = max(action_severity, 1)
                plan["reason"].append("FUNDING_BLEED")

            if holding > 24 and pnl < 0.05:
                action_severity = max(action_severity, 1)
                plan["reason"].append("TIME_DECAY")

            # --- CONSOLIDAÇÃO DO PLANO ---
            if action_severity == 2:
                plan["action"] = "HARD_EXIT"
                plan["urgency"] = "HIGH"
                plan["recommended_order_type"] = "MARKET" # Hard exit exige rapidez
            elif action_severity == 1:
                plan["action"] = "SOFT_EXIT"
                plan["urgency"] = "MEDIUM"
                plan["recommended_order_type"] = "LIMIT" # Soft exit tenta economizar taxa
            else:
                plan["action"] = "HOLD"

            return ExitEngine._finalize(op, plan)

        except Exception as e:
            logger.error(f"Erro no ExitEngine: {e}")
            op.exit_plan = {
                "action": "HOLD",
                "reason": ["EXIT_ENGINE_ERROR"]
            }
            return op

    @staticmethod
    def _finalize(op, plan):
        # Garante que reason seja única
        plan["reason"] = list(set(plan["reason"]))
        op.exit_plan = plan
        return op