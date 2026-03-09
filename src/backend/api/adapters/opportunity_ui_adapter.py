import time
from typing import List, Dict, Any
from src.backend.schemas.v1_contract import WebSocketPayloadV1, OpportunitySchemaV1

class OpportunityUIAdapter:
    """
    Transforma objetos internos no formato estrito 'opps.v1'.
    """
    @staticmethod
    def to_contract_payload(
        opportunities: List[Any],
        cycle_id: int,
        counts: Dict[str, int],
        timing: Dict[str, int],
        active_exchanges: List[str]
    ) -> str:
        items_v1 = []
        for opp in opportunities:
            # Mapeamento Seguro
            item = OpportunitySchemaV1(
                id=opp.unique_id,
                symbol=opp.base_currency,
                pair=f"{opp.base_currency}_{opp.quote_currency}",
                base=opp.base_currency,
                quote=opp.quote_currency,
                spot_exchange=opp.spot_venue,
                futures_exchange=opp.futures_venue,
                venue_mode=opp.mode,
                spot_ask=opp.spot_price_ask,
                spot_bid=opp.spot_price_bid,
                futures_bid=opp.futures_price_bid,
                futures_ask=opp.futures_price_ask,
                spread_pct=opp.spread_gross_pct,
                spread_liq_pct=opp.spread_net_pct,
                fees_pct=opp.total_fees_pct,
                slippage_pct_est=opp.slippage_est,
                pnl_close_usd=opp.estimated_pnl_usd,
                # Campos opcionais L1 (Ticket A2)
                spot_top_book_usd=getattr(opp, 'spot_l1_value', None),
                futures_top_book_usd=getattr(opp, 'futures_l1_value', None),
                spot_liq_usd=opp.liquidity_spot,
                futures_liq_usd=opp.liquidity_futures,
                capacity_usd=opp.max_capacity_usd,
                confidence=opp.confidence_score,
                score=opp.final_score,
                # status=opp.status,  # Assuming opp.status is already StatusEnum or str
                status=StatusEnum(opp.status), # Explicitly cast to Enum
                status_pt=opp.status_display_pt,
                tags=opp.tags
            )
            items_v1.append(item)

        payload = WebSocketPayloadV1(
            ts=int(time.time()),
            meta={
                "cycle": cycle_id,
                "counts": counts,
                "timing_ms": timing,
                "exchanges": active_exchanges
            },
            items=items_v1
        )
        return payload.model_dump_json()
