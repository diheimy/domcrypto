import logging

logger = logging.getLogger("OrderSizingEngine")

class OrderSizingEngine:
    """
    F5.3 - Order Size Recommendation Engine.
    Define o tamanho seguro da ordem baseado na liquidez e risco.
    """
    @staticmethod
    def calculate(op):
        try:
            # 1. Configurações Base
            SAFETY_FACTOR_BASE = 0.6  # Usa apenas 60% da liquidez disponível
            SPREAD_EFF_MIN = 0.3      # Mínimo de spread efetivo aceitável
            
            # 2. Capacidade Base (Vem do F5.2 Depth Calculator)
            base_capacity = getattr(op, 'depth_exec_usd', 0.0) * SAFETY_FACTOR_BASE
            
            # 3. Multiplicadores de Risco
            risk_mult = 1.0
            depth_flags = getattr(op, 'depth_flags', [])
            
            if "DEPTH_TRAP" in depth_flags:
                risk_mult = 0.0
            elif "THIN_DEPTH" in depth_flags:
                risk_mult = 0.4
            elif "DEPTH_STRONG" in depth_flags:
                risk_mult = 1.0
            
            # 4. Cálculo Final
            recommended = base_capacity * risk_mult
            
            # 5. Validação de Spread Efetivo
            # Se o slippage comer todo o lucro, reduzimos drasticamente a mão
            slippage_est = getattr(op, 'depth_slippage_pct', 0.0)
            spread_effective = op.spread_net_pct - slippage_est
            
            risk_level = "SAFE"
            if spread_effective < SPREAD_EFF_MIN:
                recommended *= 0.3 # Penalidade severa
                risk_level = "HIGH_RISK"
            elif risk_mult < 1.0:
                risk_level = "REDUCED"

            if recommended < 10: # Filtro de ruído
                recommended = 0.0
                risk_level = "NO_TRADE"

            # 6. Atribuição ao Modelo
            op.order_recommend_usd = round(recommended, 2)
            op.order_risk_level = risk_level
            op.order_confidence = round(risk_mult * 100, 1)

            return op

        except Exception as e:
            logger.error(f"Erro no OrderSizingEngine: {e}")
            op.order_recommend_usd = 0.0
            op.order_risk_level = "ERROR"
            return op