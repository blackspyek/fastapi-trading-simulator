from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv

from app.api.core.dependencies import (
    get_asset_service,
    get_current_user,
    require_admin,
)
from app.api.services.asset_service import AssetService
from app.api.clients.binance_client import BinanceClient
from app.api.models.user import User
from app.api.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetPriceResponse,
)
from app.api.schemas.klines import KlineResponse

router = APIRouter()


@cbv(router)
class AssetController:
    """
    REST API controller for asset operations.

    Public endpoints are available to all logged-in users.
    Modifying endpoints require administrator permissions.

    Attributes:
        asset_service: Injected asset service.
    """

    asset_service: AssetService = Depends(get_asset_service)

    @router.get("/", response_model=List[AssetPriceResponse])
    async def get_active_assets(self) -> List[AssetPriceResponse]:
        """
        Fetches list of active cryptocurrencies with their prices.

        Public endpoint - accessible without login.

        Returns:
            List of active assets with current prices.
        """
        assets = await self.asset_service.get_all_active()
        return [AssetPriceResponse.model_validate(a) for a in assets]

    @router.get("/{asset_id}", response_model=AssetResponse)
    async def get_asset(self, asset_id: int) -> AssetResponse:
        """
        Fetches details of a single asset.

        Public endpoint - accessible without login.

        Args:
            asset_id: Asset identifier.

        Returns:
            Detailed asset data.
        """
        asset = await self.asset_service.get_by_id(asset_id)
        return AssetResponse.model_validate(asset)

    @router.get("/{asset_id}/klines", response_model=List[KlineResponse])
    async def get_asset_klines(
        self,
        asset_id: int,
        interval: str = Query("1h", pattern="^(1m|5m|15m|1h|4h|1d)$"),
        limit: int = Query(100, ge=1, le=500)
    ) -> List[KlineResponse]:
        """
        Fetches candlestick (klines) data for an asset.

        Public endpoint - accessible without login.
        Data fetched directly from Binance API.

        Args:
            asset_id: Asset identifier.
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d).
            limit: Number of candles to fetch (1-500).

        Returns:
            List of OHLCV data for charting.
        """
        asset = await self.asset_service.get_by_id(asset_id)
        binance_client = BinanceClient()
        try:
            klines = await binance_client.get_klines(
                symbol=asset.binance_symbol.upper(),
                interval=interval,
                limit=limit
            )
            return [KlineResponse(**k) for k in klines]
        except Exception as e:
            print(f"Error fetching klines for {asset.binance_symbol}: {e}")
            return []


    @router.get("/admin/all", response_model=List[AssetResponse])
    async def get_all_assets(
        self, _: User = Depends(require_admin)
    ) -> List[AssetResponse]:
        """
        Fetches all assets (including inactive).

        Administrators only.

        Returns:
            List of all assets.
        """
        assets = await self.asset_service.get_all()
        return [AssetResponse.model_validate(a) for a in assets]

    @router.post("/", response_model=AssetResponse, status_code=201)
    async def create_asset(
        self, data: AssetCreate, _: User = Depends(require_admin)
    ) -> AssetResponse:
        """
        Creates a new asset for tracking.

        Administrators only.

        Args:
            data: New asset data.

        Returns:
            Created asset.
        """
        asset = await self.asset_service.create(data)
        return AssetResponse.model_validate(asset)

    @router.put("/{asset_id}", response_model=AssetResponse)
    async def update_asset(
        self, asset_id: int, data: AssetUpdate, _: User = Depends(require_admin)
    ) -> AssetResponse:
        """
        Updates an asset.

        Administrators only.

        Args:
            asset_id: Asset identifier.
            data: Update data.

        Returns:
            Updated asset.
        """
        asset = await self.asset_service.update(asset_id, data)
        return AssetResponse.model_validate(asset)

    @router.patch("/{asset_id}/toggle", response_model=AssetResponse)
    async def toggle_asset_active(
        self, asset_id: int, _: User = Depends(require_admin)
    ) -> AssetResponse:
        """
        Toggles asset active status.

        Administrators only.

        Args:
            asset_id: Asset identifier.

        Returns:
            Asset with changed status.
        """
        asset = await self.asset_service.toggle_active(asset_id)
        return AssetResponse.model_validate(asset)

    @router.delete("/{asset_id}", status_code=204)
    async def delete_asset(
        self, asset_id: int, _: User = Depends(require_admin)
    ) -> None:
        """
        Deletes an asset.

        Only for assets without transactions and portfolio.
        Administrators only.

        Args:
            asset_id: Asset identifier.
        """
        await self.asset_service.delete(asset_id)
