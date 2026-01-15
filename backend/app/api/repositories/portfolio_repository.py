"""
Portfolio repository.

Provides CRUD operations and helper methods
for the Portfolio entity in the database.
"""

from decimal import Decimal
from typing import Optional, List

from sqlalchemy import select

from app.api.repositories.base import BaseRepository
from app.api.models.portfolio import Portfolio


class PortfolioRepository(BaseRepository):
    """
    Repository for managing Portfolio entities.

    Portfolio represents a user's holding of a specific asset.
    """

    async def get_by_user_and_asset(
        self, user_id: int, asset_id: int
    ) -> Optional[Portfolio]:
        """
        Fetches a portfolio entry for a given user and asset.

        Args:
            user_id: User identifier.
            asset_id: Asset identifier.

        Returns:
            Portfolio object if found, None otherwise.
        """
        query = select(Portfolio).where(
            Portfolio.user_id == user_id,
            Portfolio.asset_id == asset_id
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_portfolio(self, user_id: int) -> List[Portfolio]:
        """
        Fetches a user's entire portfolio.

        Args:
            user_id: User identifier.

        Returns:
            List of Portfolio entries for the given user.
        """
        query = select(Portfolio).where(Portfolio.user_id == user_id)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def create(
        self, user_id: int, asset_id: int, quantity: Decimal
    ) -> Portfolio:
        """
        Creates a new portfolio entry.

        Args:
            user_id: User identifier.
            asset_id: Asset identifier.
            quantity: Initial asset quantity.

        Returns:
            Created Portfolio object.
        """
        portfolio = Portfolio(
            user_id=user_id,
            asset_id=asset_id,
            quantity=quantity
        )
        self._db.add(portfolio)
        return portfolio

    async def update_quantity(
        self, portfolio: Portfolio, quantity_delta: Decimal
    ) -> None:
        """
        Updates the asset quantity in portfolio.

        Args:
            portfolio: Portfolio object to update.
            quantity_delta: Quantity change (negative = decrease).
        """
        portfolio.quantity += quantity_delta

    async def delete_user_portfolio(self, user_id: int) -> int:
        """
        Deletes all portfolio entries for a given user.

        Args:
            user_id: User identifier.

        Returns:
            Number of deleted entries.
        """
        from sqlalchemy import delete as sql_delete

        query = sql_delete(Portfolio).where(Portfolio.user_id == user_id)
        result = await self._db.execute(query)
        return result.rowcount

    async def delete_by_asset_id(self, asset_id: int) -> int:
        """
        Deletes all portfolio entries for a specific asset.

        Args:
            asset_id: Asset identifier.

        Returns:
            Number of deleted entries.
        """
        from sqlalchemy import delete as sql_delete

        query = sql_delete(Portfolio).where(Portfolio.asset_id == asset_id)
        result = await self._db.execute(query)
        return result.rowcount

