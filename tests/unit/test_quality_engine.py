"""Tests for Quality Engine.

Following QA-SPEC.md specification.
"""

import pytest
from unittest.mock import Mock
from src.backend.services.quality.quality_engine import QualityEngine


class TestQualityEngine:
    """Test cases for QualityEngine."""

    def test_enrich_high_spread_high_volume(self):
        """Testa score alto para spread alto e volume alto."""
        op = Mock()
        op.status = "ACTIVE"
        op.spread_net_pct = 3.0
        op.volume_24h_usd = 1000000
        op.persistence_minutes = 10
        op.behavior_flags = []
        op.liquidity_flags = []
        op.depth_flags = []
        op.depth_exec_usd = 100000
        op.top_liquidity_usd = 50000
        op.tags = []
        op.score = 0
        op.quality_level = ""

        result = QualityEngine.enrich(op)

        assert result.score >= 70
        assert result.score <= 100
        assert result.quality_level in ["READY", "WATCH", "LOW_QUAL"]

    def test_enrich_low_volume(self):
        """Testa score baixo para volume baixo."""
        op = Mock()
        op.status = "ACTIVE"
        op.spread_net_pct = 2.0
        op.volume_24h_usd = 10000  # Baixo volume
        op.persistence_minutes = 0
        op.behavior_flags = []
        op.liquidity_flags = []
        op.depth_flags = []
        op.depth_exec_usd = 0
        op.top_liquidity_usd = 100
        op.tags = []
        op.score = 0
        op.quality_level = ""

        result = QualityEngine.enrich(op)

        assert result.score < 50

    def test_enrich_observation_only(self):
        """Testa que OBSERVATION_ONLY tem score zero."""
        op = Mock()
        op.status = "OBSERVATION_ONLY"
        op.spread_net_pct = 5.0
        op.volume_24h_usd = 1000000
        op.tags = []
        op.score = 100
        op.quality_level = "READY"

        result = QualityEngine.enrich(op)

        assert result.score == 0
        assert result.quality_level == "OBSERVE"

    def test_enrich_thin_book(self):
        """Testa que book fino bloqueia oportunidade."""
        op = Mock()
        op.status = "ACTIVE"
        op.spread_net_pct = 2.0
        op.volume_24h_usd = 100000
        op.persistence_minutes = 10
        op.behavior_flags = []
        op.liquidity_flags = []
        op.depth_flags = []
        op.depth_exec_usd = 0
        op.top_liquidity_usd = 10  # Book muito fino
        op.tags = []
        op.score = 80
        op.quality_level = "READY"

        result = QualityEngine.enrich(op)

        assert result.status == "BLOCKED_THIN_BOOK"
        assert result.score == 0
        assert result.quality_level == "LOW_QUAL"

    def test_enrich_negative_spread(self):
        """Testa spread negativo."""
        op = Mock()
        op.status = "ACTIVE"
        op.spread_net_pct = -0.5  # Spread negativo
        op.volume_24h_usd = 100000
        op.persistence_minutes = 10
        op.behavior_flags = []
        op.liquidity_flags = []
        op.depth_flags = []
        op.depth_exec_usd = 100000
        op.top_liquidity_usd = 50000
        op.tags = []
        op.score = 50
        op.quality_level = "WATCH"

        result = QualityEngine.enrich(op)

        assert result.score == 0
        assert result.quality_level == "LOW_QUAL"

    def test_enrich_persistence_bonus(self):
        """Testa bônus de persistência."""
        op_long = Mock()
        op_long.status = "ACTIVE"
        op_long.spread_net_pct = 1.5
        op_long.volume_24h_usd = 500000
        op_long.persistence_minutes = 15  # Alta persistência
        op_long.behavior_flags = []
        op_long.liquidity_flags = []
        op_long.depth_flags = []
        op_long.depth_exec_usd = 100000
        op_long.top_liquidity_usd = 50000
        op_long.tags = []
        op_long.score = 0
        op_long.quality_level = ""

        op_short = Mock()
        op_short.status = "ACTIVE"
        op_short.spread_net_pct = 1.5
        op_short.volume_24h_usd = 500000
        op_short.persistence_minutes = 1  # Baixa persistência
        op_short.behavior_flags = []
        op_short.liquidity_flags = []
        op_short.depth_flags = []
        op_short.depth_exec_usd = 100000
        op_short.top_liquidity_usd = 50000
        op_short.tags = []
        op_short.score = 0
        op_short.quality_level = ""

        result_long = QualityEngine.enrich(op_long)
        result_short = QualityEngine.enrich(op_short)

        # Oportunidade com mais persistência deve ter score maior
        assert result_long.score >= result_short.score

    def test_enrich_trap_behavior(self):
        """Testa penalidade para comportamento trap."""
        op = Mock()
        op.status = "ACTIVE"
        op.spread_net_pct = 2.0
        op.volume_24h_usd = 500000
        op.persistence_minutes = 10
        op.behavior_flags = ["TRAP"]  # Trap behavior
        op.liquidity_flags = []
        op.depth_flags = []
        op.depth_exec_usd = 100000
        op.top_liquidity_usd = 50000
        op.tags = []
        op.score = 0
        op.quality_level = ""

        result = QualityEngine.enrich(op)

        # Trap deve reduzir score
        assert result.score < 70

    def test_enrich_synthetic_depth_tag(self):
        """Testa penalidade para synthetic depth."""
        op = Mock()
        op.status = "ACTIVE"
        op.spread_net_pct = 2.0
        op.volume_24h_usd = 500000
        op.persistence_minutes = 10
        op.behavior_flags = []
        op.liquidity_flags = []
        op.depth_flags = []
        op.depth_exec_usd = 100000
        op.top_liquidity_usd = 50000
        op.tags = ["SYNTHETIC_DEPTH"]
        op.score = 80
        op.quality_level = "READY"

        result = QualityEngine.enrich(op)

        # Synthetic depth deve reduzir score em 30%
        assert result.score <= 56  # 80 * 0.70

    def test_enrich_score_bounds(self):
        """Testa que score está sempre entre 0 e 100."""
        op = Mock()
        op.status = "ACTIVE"
        op.spread_net_pct = 10.0  # Spread extremo
        op.volume_24h_usd = 10000000  # Volume extremo
        op.persistence_minutes = 100
        op.behavior_flags = []
        op.liquidity_flags = []
        op.depth_flags = []
        op.depth_exec_usd = 1000000
        op.top_liquidity_usd = 500000
        op.tags = []
        op.score = 0
        op.quality_level = ""

        result = QualityEngine.enrich(op)

        assert 0 <= result.score <= 100
