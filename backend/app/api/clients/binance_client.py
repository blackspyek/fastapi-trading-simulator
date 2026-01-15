import json
from typing import Dict, List, Any

import httpx


class BinanceClient:
    """
    Client for communication with Binance API.

    Provides an abstraction over HTTP requests to Binance API,
    facilitating testing and potential data provider changes.

    Attributes:
        BASE_URL: Base URL of Binance API.
        _timeout: HTTP request timeout in seconds.
    """

    BASE_URL: str = "https://api.binance.com/api/v3"

    def __init__(self, timeout: float = 10.0) -> None:
        """
        Initializes the Binance client.

        Args:
            timeout: Maximum response wait time in seconds.
        """
        self._timeout: float = timeout

    async def get_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Fetches current prices for given symbols.

        Args:
            symbols: List of Binance symbols (e.g. ["BTCUSDT", "ETHUSDT"]).

        Returns:
            Dictionary {symbol: price}, e.g. {"BTCUSDT": 45000.50}.

        Raises:
            httpx.HTTPError: On API communication error.
        """
        symbols_json: str = json.dumps(symbols, separators=(",", ":"))
        params: Dict[str, str] = {"symbols": symbols_json}

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{self.BASE_URL}/ticker/price",
                params=params
            )
            response.raise_for_status()
            data: List[Dict[str, Any]] = response.json()

        return {item["symbol"]: float(item["price"]) for item in data}

    async def get_single_price(self, symbol: str) -> float:
        """
        Fetches the price of a single symbol.

        Args:
            symbol: Binance symbol (e.g. "BTCUSDT").

        Returns:
            Current price as float.

        Raises:
            httpx.HTTPError: On API communication error.
        """
        prices = await self.get_prices([symbol])
        return prices[symbol]

    async def get_klines(
        self, symbol: str, interval: str = "1h", limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetches candlestick data (klines) for a given symbol.

        Args:
            symbol: Binance symbol (e.g. "BTCUSDT").
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d).
            limit: Number of candles to fetch (max 1000).

        Returns:
            List of dictionaries with OHLCV data:
            - time: timestamp in seconds
            - open, high, low, close: prices
            - volume: trading volume

        Raises:
            httpx.HTTPError: On API communication error.
        """
        params: Dict[str, Any] = {
            "symbol": symbol,
            "interval": interval,
            "limit": min(limit, 1000)
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{self.BASE_URL}/klines",
                params=params
            )
            response.raise_for_status()
            data: List[List[Any]] = response.json()

        # Binance returns array of arrays, we transform to dictionaries
        return [
            {
                "time": int(item[0] / 1000),  # ms -> s
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5])
            }
            for item in data
        ]
