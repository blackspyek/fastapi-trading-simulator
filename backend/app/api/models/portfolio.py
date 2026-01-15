"""
Portfolio model.

Represents a user's holding of a specific asset.
"""

from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.api.db.base import Base


class Portfolio(Base):
    """
    Portfolio entry model.

    Represents a user's holding of a specific cryptocurrency asset.
    It's the fastest way to get the user's portfolio without fetching 
        and calculating transactions.

    Attributes:
        id: Unique portfolio entry identifier.
        user_id: ID of the user who owns this holding.
        asset_id: ID of the held asset.
        quantity: Amount of the asset held.
        user: Reference to the owning user.
        asset: Reference to the held asset.
    """

    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True)

    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=0)

    user: Mapped["User"] = relationship(back_populates="portfolio")
    asset: Mapped["Asset"] = relationship(back_populates="holders")

    __table_args__ = (
        UniqueConstraint("user_id", "asset_id", name="uq_user_asset"),
    )