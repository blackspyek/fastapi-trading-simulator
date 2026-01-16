from typing import List, Optional
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models.asset import Asset
from app.api.repositories.asset_repository import AssetRepository
from app.api.repositories.portfolio_repository import PortfolioRepository
from app.api.repositories.transaction_repository import TransactionRepository
from app.api.schemas.asset import AssetCreate, AssetUpdate


class AssetService:
    """
    Service handling asset operations.

    Attributes:
        _asset_repo: Asset repository.
        _portfolio_repo: Portfolio repository.
        _transaction_repo: Transaction repository.
        _db: Database session.
    """

    async def _fetch_initial_price(self, binance_symbol: str) -> Optional[Decimal]:
        """
        Fetches initial price for asset from Binance.

        Args:
            binance_symbol: Asset symbol on Binance.

        Returns:
            Current price or None if fetch fails.
        """
        if not hasattr(self, "_binance_client"):
            return None
            
        try:
            price = await self._binance_client.get_single_price(binance_symbol)
            return Decimal(str(price))
        except Exception as e:
            print(f"Failed to fetch initial price for {binance_symbol}: {e}")
            return None

    def __init__(
        self,
        asset_repo: AssetRepository,
        portfolio_repo: PortfolioRepository,
        transaction_repo: TransactionRepository,
        price_history_repo: "PriceHistoryRepository",
        db: AsyncSession,
        binance_client: Optional[object] = None
    ) -> None:
        """
        Initializes the service with required dependencies.

        Args:
            asset_repo: Asset repository.
            portfolio_repo: Portfolio repository.
            transaction_repo: Transaction repository.
            price_history_repo: PriceHistory repository.
            db: Database session.
            binance_client: Optional BinanceClient for fetching initial data.
        """
        self._asset_repo: AssetRepository = asset_repo
        self._portfolio_repo: PortfolioRepository = portfolio_repo
        self._transaction_repo: TransactionRepository = transaction_repo
        self._price_history_repo = price_history_repo
        self._db: AsyncSession = db
        self._binance_client = binance_client

    async def get_all_active(self) -> List[Asset]:
        """
        Fetches all active assets.

        Returns:
            List of active assets.
        """
        return await self._asset_repo.get_all_active()

    async def get_all(self) -> List[Asset]:
        """
        Fetches all assets (including inactive, for admin).

        Returns:
            List of all assets.
        """
        return await self._asset_repo.get_all()

    async def get_by_id(self, asset_id: int) -> Asset:
        """
        Fetches an asset by ID.

        Args:
            asset_id: Asset identifier.

        Returns:
            Asset object.

        Raises:
            HTTPException: 404 if asset doesn't exist.
        """
        asset = await self._asset_repo.get_by_id(asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with ID {asset_id} doesn't exist."
            )
        return asset

    async def create(self, data: AssetCreate) -> Asset:
        """
        Creates a new asset.

        Args:
            data: New asset data.

        Returns:
            Created asset.

        Raises:
            HTTPException: 400 if ticker or binance_symbol already exists.
        """
        # Normalize symbols to uppercase
        data.ticker = data.ticker.upper().strip()
        data.binance_symbol = data.binance_symbol.upper().strip()

        existing = await self._asset_repo.get_by_ticker(data.ticker)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset with ticker '{data.ticker}' already exists."
            )

        existing_symbol = await self._asset_repo.get_by_binance_symbol(data.binance_symbol)
        if existing_symbol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Asset with Binance symbol '{data.binance_symbol}' already exists."
            )

        asset = await self._asset_repo.create(
            ticker=data.ticker,
            name=data.name,
            binance_symbol=data.binance_symbol
        )

        # Try to fetch initial price immediately
        initial_price = await self._fetch_initial_price(data.binance_symbol)
        if initial_price:
            asset.current_price = initial_price

        await self._db.commit()
        await self._db.refresh(asset)

        return asset

    async def update(self, asset_id: int, data: AssetUpdate) -> Asset:
        """
        Updates an asset.

        Args:
            asset_id: Asset identifier.
            data: Update data.

        Returns:
            Updated asset.
        """
        asset = await self.get_by_id(asset_id)

        if data.name is not None:
            asset.name = data.name
        if data.binance_symbol is not None:
            asset.binance_symbol = data.binance_symbol.upper().strip()
            # If symbol changes, try to update price
            initial_price = await self._fetch_initial_price(asset.binance_symbol)
            if initial_price:
                asset.current_price = initial_price
                
        if data.is_active is not None:
            asset.is_active = data.is_active

        await self._db.commit()
        await self._db.refresh(asset)

        return asset

    async def toggle_active(self, asset_id: int) -> Asset:
        """
        Toggles asset active status.

        Args:
            asset_id: Asset identifier.

        Returns:
            Asset with changed status.
        """
        asset = await self.get_by_id(asset_id)
        asset.is_active = not asset.is_active

        await self._db.commit()
        await self._db.refresh(asset)

        return asset

    async def delete(self, asset_id: int) -> None:
        """
        Deletes an asset and all related data (cascading).

        Args:
            asset_id: Asset identifier.

        Raises:
            HTTPException: 404 if asset doesn't exist.
        """
        asset = await self.get_by_id(asset_id)

        # Cascading delete of related data
        # We call delete unconditionally to avoid lazy loading issues (MissingGreenlet)
        # and because delete statements are idempotent (no-op if empty).
        await self._portfolio_repo.delete_by_asset_id(asset_id)
        await self._transaction_repo.delete_by_asset_id(asset_id)
        await self._price_history_repo.delete_by_asset_id(asset_id)

        await self._asset_repo.delete(asset)
        await self._db.commit()
