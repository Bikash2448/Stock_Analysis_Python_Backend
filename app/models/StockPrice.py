from datetime import datetime
from pydantic import BaseModel

class StockPrice(BaseModel):
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int
    updated_at: datetime