import pytest
import json
from pydantic import ValidationError
from typing import List
from app.api.adapters.opportunity_ui_adapter import OpportunityUIAdapter
from app.schemas.v1_contract import OpportunitySchemaV1, StatusEnum

# Mock simples
class MockOpp:
    def __init__(self, id="mexc:BTC_USDT", status="ACTIVE", score=99.0):
        self.unique_id = id
        self.base_currency = "BTC"
        self.quote_currency = "USDT"
        self.spot_venue = "mexc"
        self.futures_venue = "mexc_futures"
        self.mode = "same"
        self.spot_price_ask = 100.0
        self.spot_price_bid = 99.0
        self.futures_price_bid = 101.0
        self.futures_price_ask = 101.1
        self.spread_gross_pct = 1.0
        self.spread_net_pct = 0.8
        self.total_fees_pct = 0.2
        self.slippage_est = 0.1
        self.estimated_pnl_usd = 10.0
        self.liquidity_spot = 1000.0
        self.liquidity_futures = 2000.0
        self.max_capacity_usd = 500.0
        self.confidence_score = 0.95
        self.final_score = score
        self.status = status
        self.status_display_pt = "ATIVO" if status == "ACTIVE" else "BOLA"
        self.tags = ["TEST"]
        self.spot_l1_value = 5000.0
        self.futures_l1_value = 6000.0

def test_valid_payload():
    opps = [MockOpp(id="test:1")]
    payload_json = OpportunityUIAdapter.to_contract_payload(
        opportunities=opps,
        cycle_id=1,
        counts={"raw":1, "active":1, "killed":0},
        timing={"build": 10, "broadcast": 1},
        active_exchanges=["mexc"]
    )
    data = json.loads(payload_json)
    assert data["schema_version"] == "opps.v1"
    assert data["items"][0]["status"] == "ACTIVE"
    print("\n✅ Payload Válido: OK")

def test_invalid_status_fail():
    opps = [MockOpp(status="INVALIDO")]
    with pytest.raises(ValidationError):
        OpportunityUIAdapter.to_contract_payload(
            opportunities=opps,
            cycle_id=1,
            counts={"raw":1, "active":0, "killed":1},
            timing={"build":10, "broadcast":1},
            active_exchanges=["mexc"]
        )
    print("\n✅ Bloqueio de Status Inválido: OK")

if __name__ == "__main__":
    try:
        test_valid_payload()
        test_invalid_status_fail()
        print("\n🚀 TICKET A1 VALIDADO COM SUCESSO!")
    except Exception as e:
        print(f"\n❌ FALHA NOS TESTES: {e}")
