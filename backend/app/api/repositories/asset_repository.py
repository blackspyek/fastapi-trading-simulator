from decimal import Decimal
from typing import Optional, List, Dict

from sqlalchemy import select, update

from app.api.repositories.base import BaseRepository
from app.api.models.asset import Asset


class AssetRepository(BaseRepository):
    """
    Repository for managing Asset entities.

    Provides methods for fetching and updating
    assets and their prices.
    """

    async def get_by_id(self, asset_id: int) -> Optional[Asset]:
        """
        Fetches an asset by ID.

        Args:
            asset_id: Asset identifier.

        Returns:
            Asset object if found, None otherwise.
        """
        return await self._db.get(Asset, asset_id)

    async def get_by_ticker(self, ticker: str) -> Optional[Asset]:
        """
        Fetches an asset by symbol (ticker).

        Args:
            ticker: Asset symbol (e.g., BTC, ETH).

        Returns:
            Asset object if found, None otherwise.
        """
        query = select(Asset).where(Asset.ticker == ticker)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Asset]:
        """
        Fetches all assets.

        Returns:
            List of all assets.
        """
        query = select(Asset)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_ticker_to_id_map(self) -> Dict[str, int]:
        """
        Returns a ticker -> id mapping for all assets.

        Returns:
            Dictionary {ticker: asset_id}.
        """
        assets = await self.get_all()
        return {asset.ticker: asset.id for asset in assets}

    async def update_price(self, asset_id: int, new_price: Decimal) -> None:
        """
        Updates an asset's price.

        Args:
            asset_id: Asset identifier.
            new_price: New asset price.
        """
        stmt = (
            update(Asset)
            .where(Asset.id == asset_id)
            .values(current_price=new_price)
        )
        await self._db.execute(stmt)

    async def get_all_active(self) -> List[Asset]:
        """
        Fetches all active assets.

        Returns:
            List of active assets.
        """
        query = select(Asset).where(Asset.is_active == True)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_by_binance_symbol(self, binance_symbol: str) -> Optional[Asset]:
        """
        Fetches an asset by Binance symbol.

        Args:
            binance_symbol: Symbol on Binance exchange.

        Returns:
            Asset object if found, None otherwise.
        """
        query = select(Asset).where(Asset.binance_symbol == binance_symbol)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self, ticker: str, name: str, binance_symbol: str
    ) -> Asset:
        """
        Creates a new asset.

        Args:
            ticker: Asset symbol.
            name: Asset name.
            binance_symbol: Symbol on Binance.

        Returns:
            Created Asset object.
        """
        asset = Asset(
            ticker=ticker,
            name=name,
            binance_symbol=binance_symbol
        )
        self._db.add(asset)
        return asset

    async def delete(self, asset: Asset) -> None:
        """
        Deletes an asset.

        Args:
            asset: Asset object to delete.
        """
        await self._db.delete(asset)

    async def get_ticker_to_binance_map(self) -> Dict[str, str]:
        """
        Returns a ticker -> binance_symbol mapping for active assets.

        Returns:
            Dictionary {ticker: binance_symbol}.
        """
        assets = await self.get_all_active()
        return {asset.ticker: asset.binance_symbol for asset in assets}
