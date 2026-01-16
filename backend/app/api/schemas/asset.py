from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class AssetCreate(BaseModel):
    """
    Input data for creating a new asset.

    Attributes:
        ticker: Unique asset ticker (e.g., BTC).
        name: Full asset name (e.g., Bitcoin).
        binance_symbol: Symbol on Binance exchange (e.g., BTCUSDT).
    """

    ticker: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=50)
    binance_symbol: str = Field(..., min_length=1, max_length=20)


class AssetUpdate(BaseModel):
    """
    Data for updating an asset.

    Attributes:
        name: New name (optional).
        binance_symbol: New Binance symbol (optional).
        is_active: Whether the asset is active (optional).
    """

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    binance_symbol: Optional[str] = Field(None, min_length=1, max_length=20)
    is_active: Optional[bool] = None


class AssetResponse(BaseModel):
    """
    Asset data returned by the API.

    Attributes:
        id: Asset identifier.
        ticker: Asset ticker.
        name: Full asset name.
        binance_symbol: Binance symbol.
        current_price: Current price in USD.
        is_active: Whether the asset is actively tracked.
    """

    id: int
    ticker: str
    name: str
    binance_symbol: str
    current_price: float
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AssetPriceResponse(BaseModel):
    """
    Simplified response with asset price.

    Attributes:
        id: Asset identifier.
        ticker: Asset ticker.
        name: Asset name.
        current_price: Current price.
    """

    id: int
    ticker: str
    name: str
    current_price: float

    model_config = ConfigDict(from_attributes=True)