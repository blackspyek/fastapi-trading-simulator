import asyncio
import logging
from decimal import Decimal
from typing import Dict, List, Any, Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.clients.binance_client import BinanceClient
from app.api.core.socket_manager import ConnectionManager
from app.api.db.session import AsyncSessionLocal
from app.api.repositories import AssetRepository, PriceHistoryRepository

logger = logging.getLogger(__name__)


class MarketService:
    """
    Service responsible for fetching market data and updating prices.

    Integrates with Binance API for real-time price fetching
    and distributes updates via WebSocket to connected clients.
    """

    def __init__(
        self,
        binance_client: BinanceClient,
        connection_manager: ConnectionManager,
        session_factory: Callable[[], AsyncSession] | None = None
    ) -> None:
        self._binance_client: BinanceClient = binance_client
        self._connection_manager: ConnectionManager = connection_manager
        self._session_factory = session_factory or AsyncSessionLocal

    async def start_price_updates(self, interval_seconds: float = 5.0) -> None:
        """
        Starts the background price update loop.

        Args:
            interval_seconds: Interval between price updates.
        """
        logger.info("Starting background price update task.")
        while True:
            try:
                await self._update_prices()
            except asyncio.CancelledError:
                logger.info("Price update task cancelled.")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in MarketService loop: {e}", exc_info=True)

            await asyncio.sleep(interval_seconds)

    async def _update_prices(self) -> None:
        """
        Orchestrates the price update process:
        1. Fetch live data.
        2. Update DB.
        3. Broadcast to WebSocket.
        """
        async with self._session_factory() as db:
            asset_repo = AssetRepository(db)
            history_repo = PriceHistoryRepository(db)

            ticker_map = await asset_repo.get_ticker_to_binance_map()
            binance_prices = await self._fetch_live_prices(ticker_map)
            
            if not binance_prices:
                return

            assets_map = await asset_repo.get_ticker_to_id_map()
            updates_for_ws: List[Dict[str, Any]] = []

            for my_ticker, binance_symbol in ticker_map.items():
                if binance_symbol not in binance_prices or my_ticker not in assets_map:
                    continue
                
                update_data = await self._persist_asset_update(
                    asset_id=assets_map[my_ticker],
                    ticker=my_ticker,
                    price=binance_prices[binance_symbol],
                    asset_repo=asset_repo,
                    history_repo=history_repo
                )
                updates_for_ws.append(update_data)

            await db.commit()

        if updates_for_ws:
            await self._broadcast_updates(updates_for_ws)

    async def get_current_prices(self) -> List[Dict[str, Any]]:
        """
        Fetches current prices for all tracked assets

        Returns:
            List of dictionaries with ticker and price.
        """
        async with self._session_factory() as db:
            asset_repo = AssetRepository(db)
            
            ticker_map = await asset_repo.get_ticker_to_binance_map()
            prices = await self._fetch_live_prices(ticker_map)

            return [
                {"ticker": ticker, "price": prices.get(symbol, 0.0)}
                for ticker, symbol in ticker_map.items()
            ]


    async def _fetch_live_prices(self, ticker_map: Dict[str, str]) -> Dict[str, float]:
        """
        Helper: Extracts valid symbols and fetches prices from Binance.

        Args:
            ticker_map: Dictionary mapping tickers to binance symbols.

        Returns:
            Dictionary with binance symbols as keys and prices as values.
        """
        if not ticker_map:
            return {}

        binance_symbols = [
            s for s in ticker_map.values()
            if s and s.isupper() and s.isalnum()
        ]

        if not binance_symbols:
            return {}

        try:
            return await self._binance_client.get_prices(binance_symbols)
        except Exception as e:
            logger.error(f"Error fetching prices from Binance: {e}")
            return {}

    async def _persist_asset_update(
        self, 
        asset_id: int, 
        ticker: str, 
        price: float, 
        asset_repo: AssetRepository, 
        history_repo: PriceHistoryRepository
    ) -> Dict[str, Any]:
        """
        Helper: Updates single asset in DB and creates history entry.

        Args:
            asset_id: ID of the asset to update.
            ticker: Ticker of the asset.
            price: New price of the asset.
            asset_repo: Asset repository instance.
            history_repo: Price history repository instance.

        Returns:
            Dictionary with ticker and price.
        """
        decimal_price = Decimal(str(price))
        
        await asset_repo.update_price(asset_id, decimal_price)
        await history_repo.create(asset_id, decimal_price)

        return {
            "ticker": ticker,
            "price": price
        }

    async def _broadcast_updates(self, updates: List[Dict[str, Any]]) -> None:
        """
        Helper: Sends JSON message via WebSocket manager.

        Args:
            updates: List of dictionaries with ticker and price.
        """
        message = {
            "type": "market_update",
            "data": updates
        }
        await self._connection_manager.broadcast(message)