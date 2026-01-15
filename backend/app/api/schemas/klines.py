from pydantic import BaseModel, ConfigDict


class KlineResponse(BaseModel):
    """
    Data for a single price candlestick.

    Attributes:
        time: Timestamp in seconds (Unix epoch).
        open: Opening price.
        high: Highest price.
        low: Lowest price.
        close: Closing price.
        volume: Trading volume.
    """

    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    model_config = ConfigDict(from_attributes=True)