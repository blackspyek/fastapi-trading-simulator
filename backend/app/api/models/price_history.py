"""
Price history model.

Stores historical price data for assets.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Numeric, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.api.db.base import Base


class PriceHistory(Base):
    """
    Price history entry model.

    Stores a historical price record for an asset.

    Attributes:
        id: Unique price history entry identifier.
        asset_id: ID of the asset this price belongs to.
        price: Price value at the recorded time.
        timestamp: When this price was recorded.
        asset: Reference to the asset.
    """

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    asset: Mapped["Asset"] = relationship(back_populates="history")