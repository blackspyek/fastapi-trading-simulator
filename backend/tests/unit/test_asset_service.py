import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.api.services.asset_service import AssetService
from app.api.schemas.asset import AssetCreate, AssetUpdate
from app.api.models.asset import Asset


class TestAssetServiceGetAllActive:
    """Tests for get_all_active method."""

    @pytest.mark.asyncio
    async def test_given_active_assets_exist_when_get_all_active_then_list_returned(self) -> None:
        """Active assets exist -> get_all_active -> list of assets."""
        asset1 = MagicMock(spec=Asset)
        asset1.ticker = "BTC"
        asset2 = MagicMock(spec=Asset)
        asset2.ticker = "ETH"

        asset_repo = AsyncMock()
        asset_repo.get_all_active.return_value = [asset1, asset2]

        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()

        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )

        result = await service.get_all_active()

        assert len(result) == 2
        asset_repo.get_all_active.assert_called_once()


class TestAssetServiceGetById:
    """Tests for get_by_id method."""

    @pytest.mark.asyncio
    async def test_given_asset_exists_when_get_by_id_then_asset_returned(self) -> None:
        """Asset exists -> get_by_id -> asset returned."""
        asset = MagicMock(spec=Asset)
        asset.id = 1
        asset.ticker = "BTC"
        
        asset_repo = AsyncMock()
        asset_repo.get_by_id.return_value = asset
        
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()

        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        
        result = await service.get_by_id(1)
        
        assert result.ticker == "BTC"
        asset_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_given_asset_not_exists_when_get_by_id_then_exception_raised(self) -> None:
        """Asset doesn't exist -> get_by_id -> HTTPException 404."""
        asset_repo = AsyncMock()
        asset_repo.get_by_id.return_value = None
        
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()

        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.get_by_id(999)
        
        assert exc_info.value.status_code == 404


class TestAssetServiceCreate:
    """Tests for create method."""

    @pytest.mark.asyncio
    async def test_given_unique_ticker_when_create_then_asset_created(self) -> None:
        """Unique ticker -> create -> asset created."""
        new_asset = MagicMock(spec=Asset)
        new_asset.ticker = "ETH"
        new_asset.name = "Ethereum"
        
        asset_repo = AsyncMock()
        asset_repo.get_by_ticker.return_value = None
        asset_repo.get_by_binance_symbol.return_value = None
        asset_repo.create.return_value = new_asset

        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()

        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        data = AssetCreate(ticker="ETH", name="Ethereum", binance_symbol="ETHUSDT")

        result = await service.create(data)

        assert result.ticker == "ETH"
        asset_repo.create.assert_called_once()
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_given_duplicate_ticker_when_create_then_exception_raised(self) -> None:
        """Duplicate ticker -> create -> HTTPException 400."""
        existing = MagicMock(spec=Asset)
        
        asset_repo = AsyncMock()
        asset_repo.get_by_ticker.return_value = existing

        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()

        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        data = AssetCreate(ticker="BTC", name="Bitcoin", binance_symbol="BTCUSDT")
        
        with pytest.raises(HTTPException) as exc_info:
            await service.create(data)
        
        assert exc_info.value.status_code == 400
        asset_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_given_duplicate_binance_symbol_when_create_then_exception_raised(self) -> None:
        """Duplicate binance_symbol -> create -> HTTPException 400."""
        existing = MagicMock(spec=Asset)
        
        asset_repo = AsyncMock()
        asset_repo.get_by_ticker.return_value = None
        asset_repo.get_by_binance_symbol.return_value = existing
        
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()
        
        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        data = AssetCreate(ticker="BTC2", name="Bitcoin 2", binance_symbol="BTCUSDT")
        
        with pytest.raises(HTTPException) as exc_info:
            await service.create(data)
        
        assert exc_info.value.status_code == 400


class TestAssetServiceToggleActive:
    """Tests for toggle_active method."""

    @pytest.mark.asyncio
    async def test_given_active_asset_when_toggle_then_deactivated(self) -> None:
        """Active asset -> toggle_active -> deactivated."""
        asset = MagicMock(spec=Asset)
        asset.id = 1
        asset.is_active = True
        
        asset_repo = AsyncMock()
        asset_repo.get_by_id.return_value = asset
        
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()
        
        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        
        await service.toggle_active(1)
        
        assert asset.is_active is False
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_given_inactive_asset_when_toggle_then_activated(self) -> None:
        """Inactive asset -> toggle_active -> activated."""
        asset = MagicMock(spec=Asset)
        asset.id = 1
        asset.is_active = False
        
        asset_repo = AsyncMock()
        asset_repo.get_by_id.return_value = asset
        
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()
        
        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        
        await service.toggle_active(1)
        
        assert asset.is_active is True
        db.commit.assert_called_once()


class TestAssetServiceGetAll:
    """Tests for get_all method."""

    @pytest.mark.asyncio
    async def test_given_assets_exist_when_get_all_then_list_returned(self) -> None:
        """Assets exist -> get_all -> list of all assets."""
        asset1 = MagicMock(spec=Asset)
        asset2 = MagicMock(spec=Asset)
        
        asset_repo = AsyncMock()
        asset_repo.get_all.return_value = [asset1, asset2]
        
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()
        
        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        
        result = await service.get_all()
        
        assert len(result) == 2
        asset_repo.get_all.assert_called_once()


class TestAssetServiceUpdate:
    """Tests for update method."""

    @pytest.mark.asyncio
    async def test_given_valid_data_when_update_then_asset_updated(self) -> None:
        """Valid data -> update -> asset fields updated."""
        asset = MagicMock(spec=Asset)
        asset.id = 1
        asset.name = "Old Name"
        
        asset_repo = AsyncMock()
        asset_repo.get_by_id.return_value = asset
        
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()
        
        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        data = AssetUpdate(name="New Name")
        
        await service.update(1, data)
        
        assert asset.name == "New Name"
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_given_asset_not_exists_when_update_then_exception_raised(self) -> None:
        """Asset doesn't exist -> update -> HTTPException 404."""
        asset_repo = AsyncMock()
        asset_repo.get_by_id.return_value = None
        
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()
        
        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        data = AssetUpdate(name="New Name")
        
        with pytest.raises(HTTPException) as exc_info:
            await service.update(999, data)
        
        assert exc_info.value.status_code == 404



class TestAssetServiceDelete:
    """Tests for delete method."""

    @pytest.mark.asyncio
    async def test_given_asset_when_delete_then_all_related_data_deleted(self) -> None:
        """Asset exists -> delete -> all related data deleted (cascade)."""
        asset = MagicMock(spec=Asset)
        asset.id = 1
        
        asset_repo = AsyncMock()
        asset_repo.get_by_id.return_value = asset
        portfolio_repo = AsyncMock()
        transaction_repo = AsyncMock()
        price_history_repo = AsyncMock()
        
        db = AsyncMock()
        service = AssetService(
            asset_repo=asset_repo,
            portfolio_repo=portfolio_repo,
            transaction_repo=transaction_repo,
            price_history_repo=price_history_repo,
            db=db
        )
        
        await service.delete(1)
        
        portfolio_repo.delete_by_asset_id.assert_called_once_with(1)
        transaction_repo.delete_by_asset_id.assert_called_once_with(1)
        price_history_repo.delete_by_asset_id.assert_called_once_with(1)
        asset_repo.delete.assert_called_once_with(asset)
        db.commit.assert_called_once()
