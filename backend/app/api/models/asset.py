"""
Asset (cryptocurrency) model.

Represents a cryptocurrency tracked in the system.
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy import String, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.db.base import Base


class Asset(Base):
    """
    Asset (cryptocurrency) model in the system.

    Attributes:
        id: Unique asset identifier.
        ticker: Asset symbol (e.g., BTC, ETH).
        name: Full asset name (e.g., Bitcoin).
        binance_symbol: Symbol on Binance exchange (e.g., BTCUSDT).
        current_price: Current price in USD.
        is_active: Whether the asset is actively tracked.
        history: Asset's price history.
        transactions: Transactions related to the asset.
        holders: Users holding the asset.
    """

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    binance_symbol: Mapped[str] = mapped_column(String(20), unique=True)
    current_price: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    history: Mapped[List["PriceHistory"]] = relationship(back_populates="asset")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="asset")
    holders: Mapped[List["Portfolio"]] = relationship(back_populates="asset")