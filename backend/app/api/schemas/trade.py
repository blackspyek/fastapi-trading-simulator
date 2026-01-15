from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class TradeRequest(BaseModel):
    """
    Input data for placing a trade order.

    Attributes:
        asset_ticker: Asset ticker symbol (e.g., BTC, ETH).
        amount: Amount to buy or sell (must be positive).
    """
    asset_ticker: str = Field(..., description="Asset ticker symbol, e.g., BTC, ETH")
    amount: Decimal = Field(..., gt=0, description="Amount to buy or sell")

class TransactionResponse(BaseModel):
    """
    Data returned after a successful transaction.

    Attributes:
        id: Transaction identifier.
        user_id: User identifier.
        asset_id: Asset identifier.
        ticker: Asset ticker symbol.
        amount: Amount of asset traded.
        price_at_transaction: Price at the time of transaction.
        type: Type of transaction (BUY or SELL).
        timestamp: Timestamp of the transaction.
    """
    id: int
    user_id: int
    asset_id: int
    ticker: str
    amount: Decimal
    price_at_transaction: Decimal
    type: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)