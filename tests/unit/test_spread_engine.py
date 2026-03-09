"""Tests for Spread Engine.

Following QA-SPEC.md specification.
"""

import pytest
from src.backend.models.spread_engine import SpreadEngine, SpreadDirection


class TestSpreadEngine:
    """Test cases for SpreadEngine."""

    def test_calculate_contango(self):
        """Testa cálculo em mercado contango (futures > spot)."""
        spot_price = 100.0
        futures_price = 101.5

        result = SpreadEngine.calculate(spot_price, futures_price)

        assert result is not None
        assert result["spread_pct"] == pytest.approx(1.5, rel=0.01)
        assert result["direction"] == SpreadDirection.SPOT_TO_FUTURES
        assert result["raw_spread"] == pytest.approx(1.5, rel=0.01)

    def test_calculate_backwardation(self):
        """Testa cálculo em mercado backwardation (futures < spot)."""
        spot_price = 100.0
        futures_price = 99.0

        result = SpreadEngine.calculate(spot_price, futures_price)

        assert result is not None
        assert result["spread_pct"] == pytest.approx(1.0, rel=0.01)
        assert result["direction"] == SpreadDirection.FUTURES_TO_SPOT
        assert result["raw_spread"] == pytest.approx(-1.0, rel=0.01)

    def test_calculate_equal_prices(self):
        """Testa cálculo com preços iguais."""
        spot_price = 100.0
        futures_price = 100.0

        result = SpreadEngine.calculate(spot_price, futures_price)

        assert result is not None
        assert result["spread_pct"] == 0.0
        assert result["direction"] == SpreadDirection.SPOT_TO_FUTURES

    def test_calculate_invalid_spot_price(self):
        """Testa cálculo com preço spot inválido (zero)."""
        spot_price = 0.0
        futures_price = 100.0

        result = SpreadEngine.calculate(spot_price, futures_price)

        assert result is None

    def test_calculate_negative_price(self):
        """Testa cálculo com preço negativo."""
        spot_price = -100.0
        futures_price = 100.0

        result = SpreadEngine.calculate(spot_price, futures_price)

        assert result is None

    def test_calculate_high_spread(self):
        """Testa cálculo com spread alto."""
        spot_price = 50000.0
        futures_price = 51000.0

        result = SpreadEngine.calculate(spot_price, futures_price)

        assert result is not None
        assert result["spread_pct"] == pytest.approx(2.0, rel=0.01)

    def test_enrich_opportunity_contango(self, mocker):
        """Testa enriquecimento de oportunidade em contango."""
        mock_op = mocker.Mock()
        mock_op.spot_price = 100.0
        mock_op.futures_price = 101.5
        mock_op.tags = []

        result = SpreadEngine.enrich(mock_op)

        assert result.spread_pct == pytest.approx(1.5, rel=0.01)
        assert SpreadDirection.SPOT_TO_FUTURES.value in result.tags

    def test_enrich_opportunity_backwardation(self, mocker):
        """Testa enriquecimento de oportunidade em backwardation."""
        mock_op = mocker.Mock()
        mock_op.spot_price = 100.0
        mock_op.futures_price = 99.0
        mock_op.tags = []

        result = SpreadEngine.enrich(mock_op)

        assert result.spread_pct == pytest.approx(1.0, rel=0.01)
        assert SpreadDirection.FUTURES_TO_SPOT.value in result.tags


class TestSpreadDirection:
    """Test cases for SpreadDirection enum."""

    def test_spread_direction_values(self):
        """Testa valores do enum SpreadDirection."""
        assert SpreadDirection.SPOT_TO_FUTURES.value == "spot_to_futures"
        assert SpreadDirection.FUTURES_TO_SPOT.value == "futures_to_spot"

    def test_spread_direction_comparison(self):
        """Testa comparação de SpreadDirection."""
        direction = SpreadDirection.SPOT_TO_FUTURES
        assert direction == "spot_to_futures"
        assert direction != "futures_to_spot"
