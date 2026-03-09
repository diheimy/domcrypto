import logging
from src.backend.services.fees.fee_registry import FEE_REGISTRY, DEFAULT_FEE
from src.backend.config.settings import ESTIMATED_TOTAL_FEE

logger = logging.getLogger("FeeEngine")

class FeeEngine:
    """
    F8 — Fee Engine Institucional (Ultimate)
    Converte spread bruto em spread líquido real.
    Versão Hardened: Trata exceções, usa defaults seguros e logs estruturados.
    """
    
    @staticmethod
    def apply(op):
        try:
            # 1. Normalização de Nomes (com fallback seguro)
            spot_exch = (getattr(op, "exchange_spot", "") or "").lower().replace('_spot', '').replace('_futures', '')
            fut_exch = (getattr(op, "exchange_futures", "") or "").lower().replace('_spot', '').replace('_futures', '')

            # 2. Busca de Fees (Registro Institucional com fallback)
            spot_fee_pct = FEE_REGISTRY.get(spot_exch, DEFAULT_FEE).get("spot", DEFAULT_FEE["spot"])
            fut_fee_pct = FEE_REGISTRY.get(fut_exch, DEFAULT_FEE).get("futures", DEFAULT_FEE["futures"])

            # Padrão
            total_fee_pct = spot_fee_pct + fut_fee_pct

            # 3. Cálculos de Spread (com getattr seguro)
            spread_gross_pct = getattr(op, "spread_exec_pct", getattr(op, "spread_pct", 0.0))
            spread_net_pct = spread_gross_pct - total_fee_pct

            # 4. Cálculo de Valor Nominal (USD)
            position_size = getattr(op, "order_recommend_usd", 0.0)
            fees_total_usd = position_size * (total_fee_pct / 100.0)
            spread_net_usd = position_size * (spread_net_pct / 100.0)

            # 5. Persistência no Modelo (com segurança)
            op.fee_spot_pct = spot_fee_pct
            op.fee_futures_pct = fut_fee_pct
            
            # Padrão Oficial
            op.fees_total_pct = total_fee_pct
            op.fees_total_usd = fees_total_usd
            
            # Legado (Frontend)
            op.total_fees_pct = total_fee_pct 
            op.total_fees_usd = fees_total_usd 

            op.spread_gross_pct = spread_gross_pct
            op.spread_net_pct = spread_net_pct
            op.spread_net_usd = spread_net_usd

            # 6. Tagging Institucional (Blindado)
            if spread_net_pct <= 0:
                # Garante lista mutável segura
                if not hasattr(op, 'tags') or op.tags is None:
                    op.tags = []
                
                if "FEE_BLOCKED" not in op.tags:
                    op.tags.append("FEE_BLOCKED")
                
                op.status = "OBSERVATION_ONLY"
                
                # Não sobrescrever se já for pior (BLOCKED/ERROR)
                current_qual = getattr(op, "quality_level", "")
                if current_qual not in ["AVOID", "BLOCKED"]:
                     op.quality_level = "OBSERVE"

            return op

        except Exception as e:
            # Log Estruturado (Melhoria Solicitada)
            symbol_ctx = getattr(op, "symbol", "UNKNOWN")
            logger.warning(
                f"⚠️ FEE_FALLBACK_USED: Erro de cálculo para {symbol_ctx}. Usando estimativa segura. Motivo: {e}",
                extra={"symbol": symbol_ctx, "error": str(e)}
            )
            
            # Fallback Institucional Seguro:
            # Assume fee estimada do sistema e rebaixa status
            op.fees_total_pct = ESTIMATED_TOTAL_FEE
            op.total_fees_pct = ESTIMATED_TOTAL_FEE
            
            # Garante lista segura antes do append
            if not hasattr(op, 'tags') or op.tags is None: 
                op.tags = []
            
            op.tags.append("FEE_ENGINE_ERROR")
            
            op.status = "OBSERVATION_ONLY"
            op.quality_level = "OBSERVE"
            
            return op