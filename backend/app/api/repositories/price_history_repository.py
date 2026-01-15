"""
Price history repository.

Provides operations for saving and fetching
asset price history.
"""

from decimal import Decimal
from typing import List
from datetime import datetime, timedelta

from sqlalchemy import select

from app.api.repositories.base import BaseRepository
from app.api.models.price_history import PriceHistory


class PriceHistoryRepository(BaseRepository):
    """
    Repository for managing asset price history.

    Enables saving price snapshots and fetching
    historical data for analysis.
    """

    async def create(self, asset_id: int, price: Decimal) -> PriceHistory:
        """
        Saves a new price history entry.

        Args:
            asset_id: Asset identifier.
            price: Price to save.

        Returns:
            Created PriceHistory object.
        """
        entry = PriceHistory(asset_id=asset_id, price=price)
        self._db.add(entry)
        return entry

    async def get_asset_history(
        self,
        asset_id: int,
        hours: int = 24,
        limit: int = 1000
    ) -> List[PriceHistory]:
        """
        Fetches asset price history from a specified period.

        Args:
            asset_id: Asset identifier.
            hours: Number of hours back.
            limit: Maximum number of entries.

        Returns:
            List of PriceHistory entries sorted chronologically.
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        query = (
            select(PriceHistory)
            .where(
                PriceHistory.asset_id == asset_id,
                PriceHistory.timestamp >= since
            )
            .order_by(PriceHistory.timestamp.asc())
            .limit(limit)
        )
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def delete_by_asset_id(self, asset_id: int) -> int:
        """
        Deletes all price history entries for a specific asset.

        Args:
            asset_id: Asset identifier.

        Returns:
            Number of deleted entries.
        """
        from sqlalchemy import delete as sql_delete

        query = sql_delete(PriceHistory).where(PriceHistory.asset_id == asset_id)
        result = await self._db.execute(query)
        return result.rowcount
