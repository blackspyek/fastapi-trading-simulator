"""
Transaction model.

Represents a buy or sell transaction in the trading system.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.api.db.base import Base


class Transaction(Base):
    """
    Transaction model.

    Represents a single buy or sell operation of an asset by a user.

    Attributes:
        id: Unique transaction identifier.
        user_id: ID of the user who made the transaction.
        asset_id: ID of the traded asset.
        amount: Quantity of the asset in the transaction.
        price_at_transaction: Asset price at the time of transaction.
        type: Transaction type (BUY or SELL).
        timestamp: When the transaction occurred.
        user: Reference to the user.
        asset: Reference to the asset.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))

    amount: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    price_at_transaction: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    type: Mapped[str] = mapped_column(String(10))

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="transactions")
    asset: Mapped["Asset"] = relationship(back_populates="transactions")