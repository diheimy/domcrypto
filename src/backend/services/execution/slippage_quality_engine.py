import logging

logger = logging.getLogger("SlippageQuality")

class SlippageQualityEngine:
    """
    F11 — Slippage & Execution Quality Engine (Institutional MVP)
    Audita execução real vs plano esperado e retroalimenta qualidade.
    Calcula Slippage, Fill Ratio, Latência e Score de Qualidade.
    """
    
    @staticmethod
    def apply(op, execution_result: dict):
        try:
            if not execution_result or not isinstance(execution_result, dict):
                return op

            # --- Extração segura dos dados do F7 ---
            req_price = execution_result.get("requested_price")
            fill_price = execution_result.get("avg_fill_price")
            filled_usd = execution_result.get("filled_usd", 0.0)
            requested_usd = execution_result.get("requested_usd", 0.0)
            latency_ms = execution_result.get("latency_ms", 0)
            fees_paid = execution_result.get("fees_paid_usd", 0.0)
            status = execution_result.get("status", "UNKNOWN")

            # --- Guard rails: Se dados cruciais faltam, aborta auditoria ---
            if not req_price or not fill_price or requested_usd <= 0:
                op.slippage_pct = 0.0
                op.fill_ratio = 0.0
                op.execution_quality_score = 0
                op.exec_flags = ["INSUFFICIENT_EXEC_DATA"]
                return op

            # --- 1. Cálculo de Slippage ---
            # Diferença percentual entre o preço pedido e o preço médio executado
            # (fill - req) / req. 
            # Nota: Para qualidade, usamos o valor absoluto (precisão).
            slippage_pct = ((fill_price - req_price) / req_price) * 100

            # --- 2. Fill Ratio (Eficiência de Liquidez) ---
            fill_ratio = min(filled_usd / requested_usd, 1.0)

            # --- 3. Exec Efficiency (Métrica Sintética 0-1) ---
            efficiency = fill_ratio
            
            # Penalidade por latência alta (> 1.5s)
            if latency_ms > 1500:
                efficiency *= 0.7
            
            # Penalidade por slippage alto (> 0.20%)
            if abs(slippage_pct) > 0.20:
                efficiency *= 0.6

            # --- 4. Quality Score (0-100) ---
            # Começa em 100 e perde pontos por falhas
            quality_score = 100
            quality_score -= abs(slippage_pct) * 200     # 0.1% slippage = -20 pontos
            quality_score -= (1 - fill_ratio) * 50       # 50% fill = -25 pontos
            quality_score -= min(latency_ms / 100, 20)   # 200ms = -2 pontos (Max -20)

            quality_score = max(0, min(int(quality_score), 100))

            # --- 5. Flags Institucionais (Alertas) ---
            flags = []

            if abs(slippage_pct) > 0.30:
                flags.append("HIGH_SLIPPAGE")

            if fill_ratio < 0.7:
                flags.append("LOW_FILL_RATIO")

            if latency_ms > 1200:
                flags.append("HIGH_LATENCY")

            if status != "FILLED":
                flags.append(f"STATUS_{status}")

            # --- Persistência no OP ---
            op.slippage_pct = round(slippage_pct, 4)
            op.fill_ratio = round(fill_ratio, 3)
            op.execution_latency_ms = latency_ms
            op.exec_efficiency = round(efficiency, 3)
            op.execution_quality_score = quality_score
            op.exec_flags = flags
            op.execution_status = status
            op.execution_fees_usd = fees_paid

            return op

        except Exception as e:
            logger.error(f"Erro no SlippageQualityEngine: {e}")
            op.exec_flags = ["F11_ERROR"]
            return op