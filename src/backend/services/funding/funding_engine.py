import logging
from src.backend.services.funding.funding_registry import (
    FUNDING_REGISTRY,
    DEFAULT_FUNDING
)

logger = logging.getLogger("FundingEngine")

class FundingEngine:
    """
    F8.1 — Funding Engine Institucional (Refined)
    Ajusta spread líquido considerando funding real de perpétuos.
    
    Refinamentos:
    - [3.1] Tag FUNDING_NEUTRAL / NO_FUNDING_DATA
    - [3.2] Blindagem contra dupla aplicação (_funding_applied)
    - [3.3] Rastreabilidade (spread_net_pct_before_funding)
    """
    
    @staticmethod
    def apply(op):
        try:
            # [REFINAMENTO 3.2] Blindagem contra dupla aplicação
            if getattr(op, "_funding_applied", False):
                return op

            # [FIX] Inicializa campos críticos com segurança (evita AttributeError)
            op.spread_net_usd = getattr(op, "spread_net_usd", 0.0)
            
            # Garante que tags é uma lista
            if not hasattr(op, "tags") or not isinstance(op.tags, list):
                op.tags = []

            # 1️⃣ Só aplica se houver futuros
            if not getattr(op, "exchange_futures", None):
                return op

            # 2️⃣ Funding rate precisa existir (em %)
            funding_rate_pct = getattr(op, "funding_rate_pct", None)
            
            if funding_rate_pct is None:
                # [MELHORIA] Se não tem dados, assume neutro e marca tag de aviso
                funding_rate_pct = 0.0
                if "NO_FUNDING_DATA" not in op.tags: 
                    op.tags.append("NO_FUNDING_DATA")

            # 3️⃣ Normalização da exchange
            fut_exch = (
                (op.exchange_futures or "").lower()
                .replace("_spot", "")
                .replace("_futures", "")
            )

            cfg = FUNDING_REGISTRY.get(fut_exch, DEFAULT_FUNDING)
            period_hours = cfg.get("period_hours", 8)

            # 4️⃣ Tempo estimado de holding (fallback seguro)
            holding_hours = getattr(op, "expected_holding_hours", 8)

            # 5️⃣ Funding proporcional ao tempo
            # LOGICA INVERTIDA PARA ARBITRAGEM:
            # - Rate > 0: Short recebe (Ganho) -> custo negativo
            # - Rate < 0: Short paga (Custo) -> custo positivo
            funding_cost_pct = -(funding_rate_pct * (holding_hours / period_hours))

            # [REFINAMENTO 3.3] Campo explícito de referência (Auditoria)
            spread_net_pct_before = getattr(op, "spread_net_pct", 0.0)
            op.spread_net_pct_before_funding = spread_net_pct_before

            # 6️⃣ Ajuste no spread líquido
            spread_net_pct_after_funding = spread_net_pct_before - funding_cost_pct

            # 7️⃣ Cálculo financeiro
            notional_usd = getattr(op, "order_recommend_usd", 0.0) or \
                           getattr(op, "top_liquidity_usd", 0.0)
            
            if notional_usd == float('inf'): notional_usd = 0.0

            funding_usd = (notional_usd * funding_cost_pct) / 100

            # 8️⃣ Persistência
            op.funding_rate_pct = funding_rate_pct
            op.funding_cost_pct = funding_cost_pct
            op.funding_cost_usd = funding_usd

            op.spread_net_pct = spread_net_pct_after_funding
            op.spread_net_usd = (notional_usd * spread_net_pct_after_funding) / 100

            # 9️⃣ Tags institucionais
            if funding_cost_pct > 0:
                if "FUNDING_NEGATIVE" not in op.tags: op.tags.append("FUNDING_NEGATIVE")
            elif funding_cost_pct < 0:
                if "FUNDING_POSITIVE" not in op.tags: op.tags.append("FUNDING_POSITIVE")
            else:
                if "FUNDING_NEUTRAL" not in op.tags: op.tags.append("FUNDING_NEUTRAL")

            # 🔟 Kill switch institucional
            # Se o spread virar negativo após funding, degrada para observação, mas não deleta
            if spread_net_pct_after_funding <= 0:
                op.status = "OBSERVATION_ONLY"
                
                current_qual = getattr(op, "quality_level", "")
                if current_qual not in ("BLOCKED", "ERROR", "BLOCKED_THIN_BOOK"):
                    op.quality_level = "OBSERVE"

                if "FUNDING_BLOCKED" not in op.tags:
                    op.tags.append("FUNDING_BLOCKED")

            # [REFINAMENTO 3.2] Marca como aplicado com sucesso
            op._funding_applied = True

            return op

        except Exception as e:
            logger.error(f"Erro no FundingEngine: {e}")
            return op