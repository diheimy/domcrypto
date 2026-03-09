"""Database models using SQLAlchemy.

Following BACKEND-SPEC.md database schema specification.
"""

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# =============================================================================
# OPPORTUNITIES
# =============================================================================

class OpportunityModel(Base):
    """Opportunity model - stores current arbitrage opportunities.

    Table schema follows BACKEND-SPEC.md specification.
    """

    __tablename__ = "opportunities"

    # Composite primary key
    symbol = Column(String(20), primary_key=True, nullable=False)
    exchange_spot = Column(String(30), primary_key=True, nullable=False)
    exchange_futures = Column(String(30), primary_key=True, nullable=False)

    # JSONB payload with full opportunity data
    payload = Column(JSONB, nullable=False, default=dict)

    # Indexed fields for fast queries
    score = Column(Integer, nullable=False, default=0)
    spread_net_pct = Column(Float, nullable=False, default=0)
    volume_24h_usd = Column(BigInteger, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="OBSERVATION_ONLY")
    capacity_band = Column(String(10), nullable=False, default="RED")

    # Timestamps
    first_seen_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_opportunities_score", "score"),
        Index("idx_opportunities_status", "status"),
        Index("idx_opportunities_spread", "spread_net_pct"),
        Index("idx_opportunities_volume", "volume_24h_usd"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "symbol": self.symbol,
            "exchange_spot": self.exchange_spot,
            "exchange_futures": self.exchange_futures,
            "payload": self.payload,
            "score": self.score,
            "spread_net_pct": self.spread_net_pct,
            "volume_24h_usd": self.volume_24h_usd,
            "status": self.status,
            "capacity_band": self.capacity_band,
            "first_seen_at": self.first_seen_at.isoformat() if self.first_seen_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# =============================================================================
# PIPELINE SNAPSHOTS
# =============================================================================

class PipelineSnapshotModel(Base):
    """Pipeline snapshot model - stores historical pipeline metrics.

    Table schema follows BACKEND-SPEC.md specification.
    """

    __tablename__ = "pipeline_snapshots"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    cycle_id = Column(Integer, nullable=False)
    ts = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    count_raw = Column(Integer, nullable=False, default=0)
    count_active = Column(Integer, nullable=False, default=0)
    count_obs = Column(Integer, nullable=False, default=0)
    count_killed = Column(Integer, nullable=False, default=0)
    top_spread = Column(Float, nullable=True)
    top_symbol = Column(String(20), nullable=True)
    meta = Column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_snapshots_cycle", "cycle_id"),
        Index("idx_snapshots_ts", "ts"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "cycle_id": self.cycle_id,
            "ts": self.ts.isoformat() if self.ts else None,
            "count_raw": self.count_raw,
            "count_active": self.count_active,
            "count_obs": self.count_obs,
            "count_killed": self.count_killed,
            "top_spread": self.top_spread,
            "top_symbol": self.top_symbol,
            "meta": self.meta,
        }


# =============================================================================
# USER SETTINGS
# =============================================================================

class UserSettingsModel(Base):
    """User settings model - stores user configurations.

    Table schema follows BACKEND-SPEC.md specification.
    """

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_name = Column(String(50), nullable=False, unique=True, default="default")
    settings = Column(JSONB, nullable=False, default=dict)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "profile_name": self.profile_name,
            "settings": self.settings,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# =============================================================================
# PnL RECORDS
# =============================================================================

class PnLRecordModel(Base):
    """PnL record model - stores trading history.

    Table schema follows BACKEND-SPEC.md specification.
    """

    __tablename__ = "pnl_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    exchange_spot = Column(String(30), nullable=False)
    exchange_futures = Column(String(30), nullable=False)
    entry_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    exit_at = Column(TIMESTAMP(timezone=True), nullable=True)
    entry_spread = Column(Float, nullable=True)
    exit_spread = Column(Float, nullable=True)
    capital_usd = Column(Float, nullable=True)
    pnl_usd = Column(Float, nullable=True)
    pnl_pct = Column(Float, nullable=True)
    fees_usd = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="OPEN", index=True)
    meta = Column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_pnl_entry_at", "entry_at"),
        Index("idx_pnl_status", "status"),
        Index("idx_pnl_symbol", "symbol"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "exchange_spot": self.exchange_spot,
            "exchange_futures": self.exchange_futures,
            "entry_at": self.entry_at.isoformat() if self.entry_at else None,
            "exit_at": self.exit_at.isoformat() if self.exit_at else None,
            "entry_spread": self.entry_spread,
            "exit_spread": self.exit_spread,
            "capital_usd": self.capital_usd,
            "pnl_usd": self.pnl_usd,
            "pnl_pct": self.pnl_pct,
            "fees_usd": self.fees_usd,
            "status": self.status,
            "meta": self.meta,
        }


# =============================================================================
# DATABASE HELPER FUNCTIONS
# =============================================================================

def create_tables(engine):
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables(engine):
    """Drop all tables."""
    Base.metadata.drop_all(bind=engine)
