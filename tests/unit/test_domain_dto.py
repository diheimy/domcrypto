"""Tests for Domain DTOs.

Following QA-SPEC.md specification.
"""

import pytest
import time
from src.backend.domain.opportunity_dto import OpportunityItemV2, OpportunityDTOv1


class TestOpportunityItemV2:
    """Test cases for OpportunityItemV2."""

    def test_create_valid_opportunity(self):
        """Testa criação de oportunidade válida."""
        opp = OpportunityItemV2(
            id="BTC-binance-binance_futures",
            symbol="BTC",
            pair="BTC/USDT",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            is_cross_venue=False,
            price_spot=50000.0,
            price_futures=50500.0,
            spread_exec_pct=1.0,
            spread_net_pct=0.8,
        )

        assert opp.symbol == "BTC"
        assert opp.spread_net_pct == 0.8
        assert opp.status == "OBSERVATION_ONLY"
        assert opp.score == 0
        assert opp.capacity_band == "RED"

    def test_opportunity_to_dict(self):
        """Testa conversão para dicionário."""
        opp = OpportunityItemV2(
            id="ETH-binance-binance_futures",
            symbol="ETH",
            pair="ETH/USDT",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            is_cross_venue=False,
            price_spot=3000.0,
            price_futures=3050.0,
            spread_exec_pct=1.5,
            spread_net_pct=1.3,
        )

        data = opp.to_dict()

        assert data["id"] == "ETH-binance-binance_futures"
        assert data["symbol"] == "ETH"
        assert data["spread_net_pct"] == 1.3
        assert isinstance(data, dict)

    def test_opportunity_default_values(self):
        """Testa valores padrão da oportunidade."""
        opp = OpportunityItemV2(
            id="BTC-binance-binance_futures",
            symbol="BTC",
            pair="BTC/USDT",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            is_cross_venue=False,
            price_spot=50000.0,
            price_futures=50500.0,
            spread_exec_pct=1.0,
            spread_net_pct=0.8,
        )

        assert opp.roi_net_pct == 0.0
        assert opp.profit_usd == 0.0
        assert opp.capacity_pct == 0.0
        assert opp.volume_24h_usd == 0.0
        assert opp.funding_rate == 0.0
        assert opp.funding_interval_hours == 8
        assert opp.score == 0
        assert opp.trust_score == 0
        assert opp.tags == []

    def test_opportunity_active_status(self):
        """Testa oportunidade com status ACTIVE."""
        opp = OpportunityItemV2(
            id="BTC-binance-binance_futures",
            symbol="BTC",
            pair="BTC/USDT",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            is_cross_venue=False,
            price_spot=50000.0,
            price_futures=50500.0,
            spread_exec_pct=1.0,
            spread_net_pct=0.8,
            status="ACTIVE",
            score=85,
            quality_level="READY",
        )

        assert opp.status == "ACTIVE"
        assert opp.score == 85
        assert opp.quality_level == "READY"

    def test_opportunity_cross_venue(self):
        """Testa oportunidade cross-venue."""
        opp = OpportunityItemV2(
            id="BTC-binance-mexc_futures",
            symbol="BTC",
            pair="BTC/USDT",
            exchange_spot="binance",
            exchange_futures="mexc_futures",
            is_cross_venue=True,
            price_spot=50000.0,
            price_futures=50600.0,
            spread_exec_pct=1.2,
            spread_net_pct=1.0,
        )

        assert opp.is_cross_venue is True
        assert opp.exchange_spot != opp.exchange_futures

    def test_opportunity_capacity_band(self):
        """Testa bandas de capacidade."""
        opp_green = OpportunityItemV2(
            id="BTC-binance-binance_futures",
            symbol="BTC",
            pair="BTC/USDT",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            is_cross_venue=False,
            price_spot=50000.0,
            price_futures=50500.0,
            spread_exec_pct=1.0,
            spread_net_pct=0.8,
            capacity_pct=80.0,
            capacity_band="GREEN",
        )

        opp_red = OpportunityItemV2(
            id="ETH-binance-binance_futures",
            symbol="ETH",
            pair="ETH/USDT",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            is_cross_venue=False,
            price_spot=3000.0,
            price_futures=3020.0,
            spread_exec_pct=0.5,
            spread_net_pct=0.3,
            capacity_pct=10.0,
            capacity_band="RED",
        )

        assert opp_green.capacity_band == "GREEN"
        assert opp_green.capacity_pct == 80.0
        assert opp_red.capacity_band == "RED"
        assert opp_red.capacity_pct == 10.0

    def test_opportunity_with_funding(self):
        """Testa oportunidade com funding rate."""
        opp = OpportunityItemV2(
            id="BTC-binance-binance_futures",
            symbol="BTC",
            pair="BTC/USDT",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            is_cross_venue=False,
            price_spot=50000.0,
            price_futures=50500.0,
            spread_exec_pct=1.0,
            spread_net_pct=0.8,
            funding_rate=0.0001,
            funding_interval_hours=8,
            next_funding_at=int(time.time()) + 28800,
        )

        assert opp.funding_rate == 0.0001
        assert opp.funding_interval_hours == 8
        assert opp.next_funding_at is not None

    def test_opportunity_kill_reason(self):
        """Testa oportunidade com motivo de kill."""
        opp = OpportunityItemV2(
            id="BTC-binance-binance_futures",
            symbol="BTC",
            pair="BTC/USDT",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            is_cross_venue=False,
            price_spot=50000.0,
            price_futures=50500.0,
            spread_exec_pct=1.0,
            spread_net_pct=0.8,
            status="KILLED",
            kill_reason="Spread convergiu",
        )

        assert opp.status == "KILLED"
        assert opp.kill_reason == "Spread convergiu"


class TestOpportunityDTOv1:
    """Test cases for OpportunityDTOv1 (legacy)."""

    def test_create_legacy_opportunity(self):
        """Testa criação de oportunidade legada."""
        opp = OpportunityDTOv1(
            id="BTC-binance-binance_futures",
            symbol="BTC",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            spot_price=50000.0,
            futures_price=50500.0,
            spread_pct=1.0,
            spread_net_pct=0.8,
            volume_24h_usd=1000000.0,
            score=80.0,
            health_score=90.0,
            tags=["high_volume"],
            status="OBSERVED",
            timestamp="2026-03-08T00:00:00Z",
        )

        assert opp.symbol == "BTC"
        assert opp.spread_pct == 1.0
        assert opp.score == 80.0

    def test_legacy_to_dict(self):
        """Testa conversão para dicionário."""
        opp = OpportunityDTOv1(
            id="ETH-binance-binance_futures",
            symbol="ETH",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            spot_price=3000.0,
            futures_price=3050.0,
            spread_pct=1.5,
            spread_net_pct=1.3,
            volume_24h_usd=500000.0,
            score=75.0,
            health_score=85.0,
            tags=[],
            status="OBSERVED",
            timestamp="2026-03-08T00:00:00Z",
        )

        data = opp.to_dict()

        assert data["symbol"] == "ETH"
        assert data["spread_pct"] == 1.5
        assert isinstance(data, dict)
