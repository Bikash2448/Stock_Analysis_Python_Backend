from fastapi import APIRouter, Query
from typing import Optional
from datetime import date
from app.services.stock_service import StockService

stock_router = APIRouter(prefix="/stocks", tags=["Stocks"])

@stock_router.post("/ingest/{symbol}")
def ingest_stock(
    symbol: str,
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    range: Optional[str] = Query(
        None,
        description="Examples: 5y, 1y, 6m, 3m"
    )
):
    count = StockService.fetch_and_store(
        symbol=symbol,
        start=start,
        end=end,
        range_value=range
    )

    return {
        "symbol": symbol,
        "records_inserted": count
    }