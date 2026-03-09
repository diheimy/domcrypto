"""Tests for API schemas.

Following QA-SPEC.md specification.
"""

import pytest
from datetime import datetime
from src.backend.api.schemas import (
    HealthResponse,
    OpportunityItemSchema,
    OpportunitiesResponse,
    UserSettingsSchema,
    PnLRecordSchema,
    PipelineSnapshotSchema,
)


class TestHealthResponse:
    """Test HealthResponse schema."""

    def test_health_response_valid(self):
        """Testa criação de health response válido."""
        response = HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="0.2.0",
            services={"pipeline": True, "database": True}
        )

        assert response.status == "healthy"
        assert response.version == "0.2.0"
        assert response.services["pipeline"] is True

    def test_health_response_degraded(self):
        """Testa health response com status degradado."""
        response = HealthResponse(
            status="degraded",
            timestamp=datetime.utcnow(),
            version="0.2.0",
            services={"pipeline": False, "database": True}
        )

        assert response.status == "degraded"


class TestOpportunityItemSchema:
    """Test OpportunityItemSchema schema."""

    def test_opportunity_item_valid(self):
        """Testa criação de oportunidade válida."""
        opp = OpportunityItemSchema(
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
            roi_net_pct=0.7,
            profit_usd=70.0,
            capacity_pct=80.0,
            capacity_band="GREEN",
            entry_leg_usd=1000.0,
            spot_top_book_usd=50000.0,
            futures_top_book_usd=50000.0,
            volume_24h_usd=1000000.0,
            funding_rate=0.01,
            funding_interval_hours=8,
            next_funding_at=None,
            orders_to_fill_spot=1,
            orders_to_fill_fut=1,
            fill_status="FILLED",
            score=85,
            trust_score=90,
            quality_level="READY",
            status="ACTIVE",
            execution_decision="EXECUTE",
            kill_reason=None,
            persistence_minutes=10,
            tags=["high_spread"],
            ts_created=1234567890,
            ts_updated=1234567890,
        )

        assert opp.symbol == "BTC"
        assert opp.spread_net_pct == 0.8
        assert opp.score == 85
        assert opp.status == "ACTIVE"
        assert opp.capacity_band == "GREEN"

    def test_opportunity_item_minimal(self):
        """Testa oportunidade com valores mínimos."""
        opp = OpportunityItemSchema(
            id="ETH-binance-binance_futures",
            symbol="ETH",
            pair="ETH/USDT",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            is_cross_venue=False,
            price_spot=3000.0,
            price_futures=3000.0,
            spread_exec_pct=0.0,
            spread_net_pct=0.0,
            roi_net_pct=0.0,
            profit_usd=0.0,
            capacity_pct=0.0,
            capacity_band="RED",
            entry_leg_usd=0.0,
            spot_top_book_usd=0.0,
            futures_top_book_usd=0.0,
            volume_24h_usd=0.0,
            funding_rate=0.0,
            funding_interval_hours=8,
            next_funding_at=None,
            orders_to_fill_spot=0,
            orders_to_fill_fut=0,
            fill_status="PENDING",
            score=0,
            trust_score=0,
            quality_level="LOW",
            status="OBSERVATION_ONLY",
            execution_decision="HOLD",
            kill_reason=None,
            persistence_minutes=0,
            tags=[],
            ts_created=0,
            ts_updated=0,
        )

        assert opp.score == 0
        assert opp.status == "OBSERVATION_ONLY"


class TestUserSettingsSchema:
    """Test UserSettingsSchema schema."""

    def test_user_settings_default(self):
        """Testa configurações com valores padrão."""
        settings = UserSettingsSchema()

        assert settings.profile_name == "default"
        assert settings.min_spread_pct == 0.5
        assert settings.min_score == 50
        assert settings.min_volume_usd == 100000
        assert settings.bankroll_usd == 10000.0
        assert settings.allow_cross is True
        assert settings.hide_blocked is False

    def test_user_settings_custom(self):
        """Testa configurações personalizadas."""
        settings = UserSettingsSchema(
            profile_name="aggressive",
            min_spread_pct=1.0,
            min_score=70,
            min_volume_usd=500000,
            bankroll_usd=50000.0,
            spots=["binance", "bybit"],
            futures=["binance_futures"],
        )

        assert settings.profile_name == "aggressive"
        assert settings.min_spread_pct == 1.0
        assert settings.min_score == 70


class TestOpportunitiesResponse:
    """Test OpportunitiesResponse schema."""

    def test_opportunities_response_valid(self):
        """Testa resposta de oportunidades válida."""
        response = OpportunitiesResponse(
            items=[],
            meta={
                "cycle_id": 1,
                "ts": 1234567890,
                "counts": {"total": 0, "active": 0, "obs": 0, "killed": 0},
                "pipeline_latency_ms": 100.0,
            }
        )

        assert len(response.items) == 0
        assert response.meta["cycle_id"] == 1


class TestPnLRecordSchema:
    """Test PnLRecordSchema schema."""

    def test_pnl_record_open(self):
        """Testa registro de PnL aberto."""
        record = PnLRecordSchema(
            id=1,
            symbol="BTC",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            entry_at=datetime.utcnow(),
            exit_at=None,
            entry_spread=1.5,
            exit_spread=None,
            capital_usd=1000.0,
            pnl_usd=None,
            pnl_pct=None,
            fees_usd=None,
            status="OPEN",
            meta=None,
        )

        assert record.status == "OPEN"
        assert record.pnl_usd is None

    def test_pnl_record_closed(self):
        """Testa registro de PnL fechado."""
        record = PnLRecordSchema(
            id=1,
            symbol="BTC",
            exchange_spot="binance",
            exchange_futures="binance_futures",
            entry_at=datetime.utcnow(),
            exit_at=datetime.utcnow(),
            entry_spread=1.5,
            exit_spread=0.5,
            capital_usd=1000.0,
            pnl_usd=100.0,
            pnl_pct=10.0,
            fees_usd=5.0,
            status="CLOSED",
            meta=None,
        )

        assert record.status == "CLOSED"
        assert record.pnl_usd == 100.0


class TestPipelineSnapshotSchema:
    """Test PipelineSnapshotSchema schema."""

    def test_snapshot_valid(self):
        """Testa snapshot de pipeline válido."""
        snapshot = PipelineSnapshotSchema(
            id=1,
            cycle_id=100,
            ts=datetime.utcnow(),
            count_raw=50,
            count_active=10,
            count_obs=35,
            count_killed=5,
            top_spread=2.5,
            top_symbol="BTC",
            meta={"latency_ms": 150},
        )

        assert snapshot.cycle_id == 100
        assert snapshot.count_raw == 50
        assert snapshot.count_active == 10
        assert snapshot.top_spread == 2.5
