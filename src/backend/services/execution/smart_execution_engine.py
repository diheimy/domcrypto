import logging

logger = logging.getLogger("SmartExecution")

class SmartExecutionEngine:
    """
    F10 — Smart Execution Engine (Institutional Refined)
    Decide COMO executar a ordem.
    Integrado com F14 (Market Regime) para limitar agressividade.
    """
    
    @staticmethod
    def decide(op):
        try:
            plan = {
                "order_type": "LIMIT",
                "time_in_force": "GTC",
                "aggressiveness": "PASSIVE",
                "split_orders": 1,
                "reason": []
            }

            order_usd = getattr(op, "order_recommend_usd", 0.0)
            liquidity_usd = getattr(op, "top_liquidity_usd", 0.0)
            spread_net = getattr(op, "spread_net_pct", 0.0)
            score = getattr(op, "score", 0)
            funding_cost = getattr(op, "funding_cost_pct", 0.0)

            if order_usd <= 0 or liquidity_usd <= 0:
                plan["reason"].append("INVALID_SIZE_OR_LIQUIDITY")
                op.execution_plan = plan
                return op

            # Métricas Auxiliares
            liquidity_ratio = order_usd / liquidity_usd
            op.exec_liquidity_ratio = round(liquidity_ratio, 4)
            
            if spread_net <= 0.15: op.exec_spread_bucket = "LOW"
            elif spread_net <= 0.40: op.exec_spread_bucket = "MEDIUM"
            else: op.exec_spread_bucket = "HIGH"

            force_limit_only = False

            # 1. Liquidez vs Impacto
            if liquidity_ratio > 0.10:
                plan["order_type"] = "LIMIT"
                plan["aggressiveness"] = "PASSIVE"
                plan["reason"].append("HIGH_IMPACT_RISK")
                force_limit_only = True

            # 2. Spread Base logic
            if spread_net > 0.40:
                if not force_limit_only:
                    plan["aggressiveness"] = "AGGRESSIVE"
                    plan["order_type"] = "MARKET"
                    plan["time_in_force"] = "IOC"
                    plan["reason"].append("HIGH_SPREAD_OPPORTUNITY")
                else:
                    plan["aggressiveness"] = "BALANCED"
                    plan["order_type"] = "LIMIT"
                    plan["time_in_force"] = "IOC"
                    plan["reason"].append("HIGH_SPREAD_BUT_IMPACT_LIMIT")

            elif spread_net > 0.15:
                if not force_limit_only:
                    plan["aggressiveness"] = "BALANCED"
                    plan["order_type"] = "LIMIT"
                    plan["time_in_force"] = "IOC"
                    plan["reason"].append("MEDIUM_SPREAD")
                else:
                    plan["aggressiveness"] = "PASSIVE"
                    plan["reason"].append("MEDIUM_SPREAD_IMPACT_PROTECT")
            else:
                plan["aggressiveness"] = "PASSIVE"
                plan["order_type"] = "LIMIT"
                plan["time_in_force"] = "GTC"
                plan["reason"].append("LOW_SPREAD")

            # 3. Score override
            if score < 60:
                plan["order_type"] = "LIMIT"
                plan["aggressiveness"] = "PASSIVE"
                plan["reason"].append("LOW_SCORE_PROTECTION")

            # 4. Funding Penalty
            if funding_cost > 0:
                if plan["aggressiveness"] == "AGGRESSIVE":
                    plan["aggressiveness"] = "BALANCED"
                plan["reason"].append("FUNDING_PENALTY")

            # 5. [F14 INTEGRATION] Market Regime Cap
            # Se o regime diz "PASSIVE", não importa o spread, a gente obedece.
            regime_factors = getattr(op, "market_regime_factors", {})
            aggressiveness_cap = regime_factors.get("aggressiveness_cap", None)

            if aggressiveness_cap:
                original_aggressiveness = plan["aggressiveness"]
                
                if aggressiveness_cap == "PASSIVE":
                    plan["aggressiveness"] = "PASSIVE"
                    # Se forçado a passivo, remove Market order se existir
                    if plan["order_type"] == "MARKET":
                        plan["order_type"] = "LIMIT"
                    if original_aggressiveness != "PASSIVE":
                        plan["reason"].append(f"REGIME_FORCED_PASSIVE")

                elif aggressiveness_cap == "BALANCED":
                    if plan["aggressiveness"] == "AGGRESSIVE":
                        plan["aggressiveness"] = "BALANCED"
                        if plan["order_type"] == "MARKET":
                            plan["order_type"] = "LIMIT"
                        plan["reason"].append(f"REGIME_CAPPED_BALANCED")

            # 6. Split logic
            if liquidity_ratio > 0.05: plan["split_orders"] = 2
            if liquidity_ratio > 0.10: plan["split_orders"] = 3

            # Coerência Final
            if plan["order_type"] == "MARKET":
                plan["aggressiveness"] = "AGGRESSIVE"

            op.execution_plan = plan
            return op

        except Exception as e:
            logger.error(f"Erro no SmartExecutionEngine: {e}")
            op.execution_plan = {
                "order_type": "LIMIT",
                "aggressiveness": "PASSIVE",
                "split_orders": 1,
                "reason": ["ERROR"]
            }
            return op