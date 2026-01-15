import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import asynccontextmanager

from app.api.services.market_service import MarketService


class TestMarketServiceUpdatePrices:
    """Tests for _update_prices method."""

    @pytest.mark.asyncio
    async def test_given_active_assets_when_update_prices_then_prices_updated_and_broadcasted(self) -> None:
        """Active assets -> _update_prices -> prices updated and WebSocket broadcast sent."""
        binance_client = AsyncMock()
        binance_client.get_prices.return_value = {
            "BTCUSDT": 45000.0,
            "ETHUSDT": 3000.0
        }
        
        connection_manager = AsyncMock()
        
        # Mock repositories
        mock_asset_repo = AsyncMock()
        mock_asset_repo.get_ticker_to_binance_map.return_value = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT"
        }
        mock_asset_repo.get_ticker_to_id_map.return_value = {
            "BTC": 1,
            "ETH": 2
        }
        
        mock_history_repo = AsyncMock()
        
        mock_db = AsyncMock()
        
        @asynccontextmanager
        async def mock_session_factory():
            yield mock_db
        
        with patch('app.api.services.market_service.AssetRepository', return_value=mock_asset_repo), \
             patch('app.api.services.market_service.PriceHistoryRepository', return_value=mock_history_repo):
            
            service = MarketService(
                binance_client=binance_client,
                connection_manager=connection_manager,
                session_factory=mock_session_factory
            )
            
            await service._update_prices()
            
            binance_client.get_prices.assert_called_once_with(["BTCUSDT", "ETHUSDT"])
            assert mock_asset_repo.update_price.call_count == 2
            assert mock_history_repo.create.call_count == 2
            mock_db.commit.assert_called_once()
            connection_manager.broadcast.assert_called_once()
            
            broadcast_call = connection_manager.broadcast.call_args[0][0]
            assert broadcast_call["type"] == "market_update"
            assert len(broadcast_call["data"]) == 2

    @pytest.mark.asyncio
    async def test_given_no_active_assets_when_update_prices_then_early_return(self) -> None:
        """No active assets -> _update_prices -> early return, no API calls."""
        binance_client = AsyncMock()
        connection_manager = AsyncMock()
        
        mock_asset_repo = AsyncMock()
        mock_asset_repo.get_ticker_to_binance_map.return_value = {}  # Empty
        
        mock_db = AsyncMock()
        
        @asynccontextmanager
        async def mock_session_factory():
            yield mock_db
        
        with patch('app.api.services.market_service.AssetRepository', return_value=mock_asset_repo):
            service = MarketService(
                binance_client=binance_client,
                connection_manager=connection_manager,
                session_factory=mock_session_factory
            )
            
            await service._update_prices()
            
            binance_client.get_prices.assert_not_called()
            connection_manager.broadcast.assert_not_called()

    @pytest.mark.asyncio
    async def test_given_binance_error_when_update_prices_then_graceful_return(self) -> None:
        """Binance API error -> _update_prices -> graceful return, no crash."""
        binance_client = AsyncMock()
        binance_client.get_prices.side_effect = Exception("Binance API error")
        
        connection_manager = AsyncMock()
        
        mock_asset_repo = AsyncMock()
        mock_asset_repo.get_ticker_to_binance_map.return_value = {"BTC": "BTCUSDT"}
        
        mock_db = AsyncMock()
        
        @asynccontextmanager
        async def mock_session_factory():
            yield mock_db
        
        with patch('app.api.services.market_service.AssetRepository', return_value=mock_asset_repo):
            service = MarketService(
                binance_client=binance_client,
                connection_manager=connection_manager,
                session_factory=mock_session_factory
            )
            
            await service._update_prices()
            
            connection_manager.broadcast.assert_not_called()
            mock_db.commit.assert_not_called()


class TestMarketServiceGetCurrentPrices:
    """Tests for get_current_prices method."""

    @pytest.mark.asyncio
    async def test_given_active_assets_when_get_current_prices_then_prices_returned(self) -> None:
        """Active assets -> get_current_prices -> list of prices."""
        binance_client = AsyncMock()
        binance_client.get_prices.return_value = {
            "BTCUSDT": 45000.0,
            "ETHUSDT": 3000.0
        }
        
        connection_manager = AsyncMock()
        
        mock_asset_repo = AsyncMock()
        mock_asset_repo.get_ticker_to_binance_map.return_value = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT"
        }
        
        mock_db = AsyncMock()
        
        @asynccontextmanager
        async def mock_session_factory():
            yield mock_db
        
        with patch('app.api.services.market_service.AssetRepository', return_value=mock_asset_repo):
            service = MarketService(
                binance_client=binance_client,
                connection_manager=connection_manager,
                session_factory=mock_session_factory
            )
            
            result = await service.get_current_prices()
            
            assert len(result) == 2
            assert {"ticker": "BTC", "price": 45000.0} in result
            assert {"ticker": "ETH", "price": 3000.0} in result

    @pytest.mark.asyncio
    async def test_given_no_active_assets_when_get_current_prices_then_empty_list(self) -> None:
        """No active assets -> get_current_prices -> empty list."""
        binance_client = AsyncMock()
        connection_manager = AsyncMock()
        
        mock_asset_repo = AsyncMock()
        mock_asset_repo.get_ticker_to_binance_map.return_value = {}
        
        mock_db = AsyncMock()
        
        @asynccontextmanager
        async def mock_session_factory():
            yield mock_db
        
        with patch('app.api.services.market_service.AssetRepository', return_value=mock_asset_repo):
            service = MarketService(
                binance_client=binance_client,
                connection_manager=connection_manager,
                session_factory=mock_session_factory
            )
            
            result = await service.get_current_prices()
            
            assert result == []
            binance_client.get_prices.assert_not_called()

    @pytest.mark.asyncio
    async def test_given_missing_price_when_get_current_prices_then_default_to_zero(self) -> None:
        """Missing price from Binance -> get_current_prices -> default to 0.0."""
        binance_client = AsyncMock()
        binance_client.get_prices.return_value = {
            "BTCUSDT": 45000.0
        }
        
        connection_manager = AsyncMock()
        
        mock_asset_repo = AsyncMock()
        mock_asset_repo.get_ticker_to_binance_map.return_value = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT"
        }
        
        mock_db = AsyncMock()
        
        @asynccontextmanager
        async def mock_session_factory():
            yield mock_db
        
        with patch('app.api.services.market_service.AssetRepository', return_value=mock_asset_repo):
            service = MarketService(
                binance_client=binance_client,
                connection_manager=connection_manager,
                session_factory=mock_session_factory
            )
            
            result = await service.get_current_prices()
            
            assert len(result) == 2
            btc_price = next(r for r in result if r["ticker"] == "BTC")
            eth_price = next(r for r in result if r["ticker"] == "ETH")
            assert btc_price["price"] == 45000.0
            assert eth_price["price"] == 0.0


class TestMarketServiceInit:
    """Tests for __init__ method."""

    def test_given_dependencies_when_init_then_attributes_set(self) -> None:
        """Dependencies provided -> __init__ -> attributes set correctly."""
        binance_client = AsyncMock()
        connection_manager = AsyncMock()
        session_factory = AsyncMock()
        
        service = MarketService(
            binance_client=binance_client,
            connection_manager=connection_manager,
            session_factory=session_factory
        )
        
        assert service._binance_client is binance_client
        assert service._connection_manager is connection_manager
        assert service._session_factory is session_factory

    def test_given_no_session_factory_when_init_then_default_used(self) -> None:
        """No session factory -> __init__ -> default AsyncSessionLocal used."""
        binance_client = AsyncMock()
        connection_manager = AsyncMock()
        
        service = MarketService(
            binance_client=binance_client,
            connection_manager=connection_manager
        )
        
        assert service._session_factory is not None
