import logging
import math

logger = logging.getLogger("CapitalAllocation")

class CapitalAllocationEngine:
    """
    V112 — Capital Allocation Engine (Zero-Hedge Support)
    - Architecture: Dual Pocket (Hedge Factor) com Capital Global.
    - Logic: Profit Gate Unificado (Total Exposure).
    - Robustness: Defense in Depth (Sanitização em todas as etapas).
    - Precision: Comparação determinística em centavos (Economic Ties).
    - Config: Hedge Factor 0.0 a 1.0 (Permite desligar capacity ou Full Bankroll).
    """

    MAX_LIQUIDITY_USAGE_PCT = 0.20
    MIN_ORDER_USD = 25.0
    
    # Haircuts de Segurança
    HAIRCUT_ESTIMATED = 0.5
    HAIRCUT_THIN      = 0.8

    # Tags Críticas
    AVOID_TAGS_CRITICAL = {
        'INVALID_PRICE_SCALE', 'ABSURD_SPREAD', 'POST_MULT_RATIO_FAIL', 
        'DEPTH_NO_TOP_LIQ', 'DEPTH_SANITY_FAIL', 'DEPTH_CALC_ERROR', 
        'KILLED'
    }

    # (A) Alocação máxima por perfil (Sobre a Capacidade de Hedge - Por Perna)
    PROFILE_MAX_ALLOC_PCT = { "AGGRESSIVE": 1.00, "MODERATE": 0.50, "CONSERVATIVE": 0.25 }

    # (B) Qualidade mínima (ROI Mínimo sobre Exposição Total)
    PROFILE_MIN_ROI_PCT = { "AGGRESSIVE": 0.005, "MODERATE": 0.010, "CONSERVATIVE": 0.012 }

    # (C) Piso Absoluto de Lucro por Perfil
    PROFILE_MIN_ABS_PROFIT_USD = { "AGGRESSIVE": 0.25, "MODERATE": 0.50, "CONSERVATIVE": 1.00 }

    SCORE_FLOOR = 20

    @staticmethod
    def _safe_float(value, default=0.0):
        try:
            if value is None: return default
            val = float(value)
            if not math.isfinite(val): return default
            return val
        except (ValueError, TypeError, OverflowError):
            return default

    @staticmethod
    def _to_cents(value):
        val = CapitalAllocationEngine._safe_float(value)
        return int(round(round(val, 2) * 100))

    @staticmethod
    def _is_financial_equal(a, b):
        return CapitalAllocationEngine._to_cents(a) == CapitalAllocationEngine._to_cents(b)

    @staticmethod
    def _analyze_data_quality(op):
        tags = getattr(op, "tags", []) or []
        risk_level = str(getattr(op, "order_risk_level", "")).upper()
        
        if isinstance(tags, list):
            tags_set = set(str(t).split(':')[0].strip().upper() for t in tags)
        else:
            tags_set = set()

        if risk_level.startswith("BLOCK"): return 0.0, f"RISK_LEVEL_{risk_level}"
        critical_match = tags_set.intersection(CapitalAllocationEngine.AVOID_TAGS_CRITICAL)
        if critical_match: return 0.0, f"CRITICAL_TAG_{list(critical_match)[0]}"
        if 'DEPTH_TRAP' in tags_set: return 0.0, "DEPTH_TRAP_DETECTED"
        if 'THIN_DEPTH' in tags_set: return CapitalAllocationEngine.HAIRCUT_THIN, None
        estimated_markers = {'NO_DEPTH_DATA', 'SIM_BOOK', 'TOP_LIQ_CLAMPED_EST'}
        if not tags_set.isdisjoint(estimated_markers): return CapitalAllocationEngine.HAIRCUT_ESTIMATED, None
            
        return 1.0, None

    @staticmethod
    def apply(op, portfolio_state):
        try:
            # 1) Hard block por status
            status_up = str(getattr(op, "status", "")).upper().strip()
            if "KILLED" in status_up:
                op.order_recommend_usd = 0.0
                op.allocation_reason = "STATUS_KILLED"
                op.execution_decision = "HOLD"
                return op

            if status_up not in ["ACTIVE", "PENDING_EXECUTION"]:
                op.order_recommend_usd = 0.0
                op.allocation_reason = "STATUS_BLOCKED"
                op.execution_decision = "HOLD"
                return op

            # [V112] DUAL POCKET MODEL (Zero-Hedge Support)
            total_capital_raw = CapitalAllocationEngine._safe_float(getattr(portfolio_state, "total_capital", 0.0))
            avail_raw = getattr(portfolio_state, "available_capital", total_capital_raw)
            available_capital_raw = CapitalAllocationEngine._safe_float(avail_raw)

            # Leitura do Hedge Factor
            hedge_factor_raw = getattr(portfolio_state, "hedge_factor", 0.5)
            hedge_factor = CapitalAllocationEngine._safe_float(hedge_factor_raw, 0.5)
            
            # [FIX] Clamp 0.0 a 1.0 (Permite desligar capacity)
            hedge_factor = max(0.0, min(1.0, hedge_factor))

            # Capacidade de Hedge
            hedging_capacity_total = total_capital_raw * hedge_factor
            hedging_capacity_available = available_capital_raw * hedge_factor

            # Telemetria
            op.allocation_hedge_factor = round(hedge_factor, 4)
            op.allocation_hedge_capacity_total = round(hedging_capacity_total, 2)
            op.allocation_hedge_capacity_available = round(hedging_capacity_available, 2)

            if hedging_capacity_total <= 0:
                op.order_recommend_usd = 0.0
                op.allocation_reason = "NO_HEDGE_CAPACITY" # Mais preciso que NO_TOTAL_CAPITAL se hedge=0
                op.execution_decision = "HOLD"
                return op

            # 2) Perfil
            profile = str(getattr(portfolio_state, "risk_profile", "AGGRESSIVE") or "AGGRESSIVE").upper().strip()
            if profile not in CapitalAllocationEngine.PROFILE_MAX_ALLOC_PCT: profile = "AGGRESSIVE"
            max_alloc_pct = CapitalAllocationEngine.PROFILE_MAX_ALLOC_PCT[profile]
            min_roi_pct = CapitalAllocationEngine.PROFILE_MIN_ROI_PCT[profile]
            min_abs_profit = CapitalAllocationEngine.PROFILE_MIN_ABS_PROFIT_USD[profile]

            # 3) Capacidade & Liquidez
            depth_exec_usd = CapitalAllocationEngine._safe_float(getattr(op, "depth_exec_usd", 0.0))
            
            if depth_exec_usd > 0:
                max_by_liquidity = depth_exec_usd
                cap_source = "DEPTH_EXEC_USD"
            else:
                top_liq = CapitalAllocationEngine._safe_float(getattr(op, "top_liquidity_usd", 0.0))
                if top_liq <= 0:
                    spot_top = CapitalAllocationEngine._safe_float(getattr(op, "spot_top_book_usd", 0.0))
                    fut_top = CapitalAllocationEngine._safe_float(getattr(op, "futures_top_book_usd", 0.0))
                    top_liq = min(spot_top, fut_top) if (spot_top > 0 and fut_top > 0) else 0.0
                max_by_liquidity = top_liq * CapitalAllocationEngine.MAX_LIQUIDITY_USAGE_PCT
                cap_source = "TOP_LIQ_FALLBACK"

            max_by_liquidity = max(0.0, CapitalAllocationEngine._safe_float(max_by_liquidity))
            haircut, block_reason = CapitalAllocationEngine._analyze_data_quality(op)
            
            if block_reason:
                op.order_recommend_usd = 0.0
                op.allocation_reason = block_reason
                op.execution_decision = "REVOKED_BY_RISK" if status_up == "PENDING_EXECUTION" else "HOLD"
                return op
            
            if haircut < 1.0:
                max_by_liquidity *= haircut
                max_by_liquidity = CapitalAllocationEngine._safe_float(max_by_liquidity)
                cap_source += f" (HAIRCUT {haircut}x)"

            # 4) Definição do Teto
            max_by_profile = hedging_capacity_total * max_alloc_pct
            max_alloc = min(max_by_profile, max_by_liquidity, hedging_capacity_available)
            max_alloc = max(0.0, CapitalAllocationEngine._safe_float(max_alloc))

            # Limiters
            limiters = []
            if CapitalAllocationEngine._is_financial_equal(max_by_profile, max_alloc): limiters.append("PROFILE")
            if CapitalAllocationEngine._is_financial_equal(max_by_liquidity, max_alloc): limiters.append("LIQUIDITY")
            if CapitalAllocationEngine._is_financial_equal(hedging_capacity_available, max_alloc): limiters.append("CAPITAL")
            
            op.allocation_limiter = "+".join(limiters) if limiters else "UNKNOWN"
            op.allocation_capped = any(x in ["LIQUIDITY", "CAPITAL"] for x in limiters)
            
            # Telemetria Perna
            op.allocation_max_usd = round(max_alloc, 2)
            
            # Telemetria Total
            max_total_usd = max_alloc * 2
            op.allocation_max_total_usd = round(max_total_usd, 2)

            if max_alloc < CapitalAllocationEngine.MIN_ORDER_USD:
                op.order_recommend_usd = 0.0
                op.allocation_reason = f"INSUFFICIENT_CAPACITY ({op.allocation_limiter})"
                op.execution_decision = "REVOKED_BY_RISK" if status_up == "PENDING_EXECUTION" else "HOLD"
                return op

            # 5) Fatores de Qualidade
            score = CapitalAllocationEngine._safe_float(getattr(op, "score", 0.0))
            if score < CapitalAllocationEngine.SCORE_FLOOR:
                op.order_recommend_usd = 0.0
                op.allocation_reason = "SCORE_BELOW_FLOOR"
                op.execution_decision = "REVOKED_BY_RISK" if status_up == "PENDING_EXECUTION" else "HOLD"
                return op

            score_factor = max(0.0, min(1.0, score / 100.0))
            funding_cost = CapitalAllocationEngine._safe_float(getattr(op, "funding_cost_pct", 0.0))
            funding_factor = 1.0
            if funding_cost > 0.05: funding_factor = 0.5
            elif funding_cost > 0.02: funding_factor = 0.7
            elif funding_cost > 0: funding_factor = 0.9

            regime_raw = CapitalAllocationEngine._safe_float(getattr(op, "market_regime_factors", {}).get("allocation_factor", 1.0), 1.0)
            quality_factor = max(0.0, min(1.0, score_factor * funding_factor * regime_raw))
            
            if quality_factor <= 0:
                op.order_recommend_usd = 0.0
                op.allocation_reason = "QUALITY_ZERO"
                op.execution_decision = "REVOKED_BY_RISK" if status_up == "PENDING_EXECUTION" else "HOLD"
                return op

            alloc_candidate = max_alloc * quality_factor
            alloc_total_usd = alloc_candidate * 2

            op.allocation_use_usd = round(alloc_candidate, 2)
            op.allocation_use_total_usd = round(alloc_total_usd, 2)

            if alloc_candidate < CapitalAllocationEngine.MIN_ORDER_USD:
                op.order_recommend_usd = 0.0
                op.allocation_reason = "BELOW_MIN_ORDER"
                op.execution_decision = "REVOKED_BY_RISK" if status_up == "PENDING_EXECUTION" else "HOLD"
                return op

            # 6) Profit Gate
            required_profit_total_usd = alloc_total_usd * min_roi_pct
            spread_exec = CapitalAllocationEngine._safe_float(getattr(op, "spread_exec_pct", 0.0))
            spread_net  = CapitalAllocationEngine._safe_float(getattr(op, "spread_net_pct", 0.0))
            profit_pct = (spread_exec if spread_exec > 0 else spread_net) / 100.0

            if profit_pct <= 0:
                op.order_recommend_usd = 0.0
                op.allocation_reason = "NO_EDGE"
                op.execution_decision = "REVOKED_BY_RISK" if status_up == "PENDING_EXECUTION" else "HOLD"
                return op

            expected_profit_total_usd = alloc_total_usd * profit_pct
            
            fail_reason = None
            if expected_profit_total_usd < required_profit_total_usd:
                fail_reason = f"PROFIT_ROI_FAIL (Exp:${expected_profit_total_usd:.2f}<Req:${required_profit_total_usd:.2f})"
            elif expected_profit_total_usd < min_abs_profit:
                fail_reason = f"PROFIT_ABS_FAIL (Exp:${expected_profit_total_usd:.2f}<Min:${min_abs_profit:.2f})"

            if fail_reason:
                op.order_recommend_usd = 0.0
                op.allocation_reason = fail_reason
                op.execution_decision = "REVOKED_BY_RISK" if status_up == "PENDING_EXECUTION" else "HOLD"
                return op

            # 7) Sucesso
            op.order_recommend_usd = round(alloc_candidate, 2)
            op.allocation_reason = "ALLOCATED"
            op.execution_decision = "PENDING_EXECUTION"
            
            return op

        except Exception as e:
            logger.error(f"Erro no CapitalAllocationEngine: {e}")
            op.order_recommend_usd = 0.0
            op.allocation_reason = "ENGINE_ERROR"
            op.execution_decision = "HOLD"
            return op