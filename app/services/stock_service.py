import yfinance as yf
from datetime import datetime, timedelta
import time
from app.repositories.stock_repository import StockRepository
from app.core.database import client

class StockService:

    @staticmethod
    def calculate_start_from_range(range_value: str):
        today = datetime.utcnow()

        if range_value.endswith("y"):
            years = int(range_value[:-1])
            return today - timedelta(days=365 * years)

        if range_value.endswith("m"):
            months = int(range_value[:-1])
            return today - timedelta(days=30 * months)

        raise ValueError("Invalid range format. Use 5y, 1y, 6m etc.")
    

    @staticmethod
    def normalize_symbol(symbol: str):
        symbol = symbol.upper()

        # If already has exchange suffix, return
        if "." in symbol:
            return symbol
        if symbol.startswith("^"):
            return symbol
            # Default to NSE
        return f"{symbol}.NS"
    

    @staticmethod
    def validate_symbol(symbol: str):
        try:
            test = yf.Ticker(symbol)
            info = test.history(period="5d")

            if info.empty:
                return False

            return True

        except Exception:
            return False
        

    # @staticmethod
    # def fetch_and_store(symbol: str, start=None, end=None, range_value=None):
        
    #     symbol = StockService.normalize_symbol(symbol)
    #     StockRepository.upsert_master(symbol)

    #     # Case 1: Custom date range
    #     if start:
    #         data = yf.download(
    #             symbol,
    #             start=start.strftime("%Y-%m-%d"),
    #             end=end.strftime("%Y-%m-%d") if end else None,
    #             interval="1d"
    #         )

    #     # Case 2: Relative range like 5y, 6m
    #     elif range_value:
    #         calculated_start = StockService.calculate_start_from_range(range_value)

    #         data = yf.download(
    #             symbol,
    #             start=calculated_start.strftime("%Y-%m-%d"),
    #             interval="1d"
    #         )

    #     # Case 3: Incremental update
    #     else:
    #         last_date = StockRepository.get_last_date(symbol)

    #         if last_date:
    #             data = yf.download(
    #                 symbol,
    #                 start=last_date.strftime("%Y-%m-%d"),
    #                 interval="1d"
    #             )
    #         else:
    #             data = yf.download(
    #                 symbol,
    #                 period="max",
    #                 interval="1d"
    #             )

    #     if data.empty:
    #         return 0

    #     inserted = StockRepository.bulk_upsert(symbol, data)
    #     time.sleep(1)

    #     return inserted



    @staticmethod
    def fetch_and_store(symbol: str, start=None, end=None, range_value=None):

        symbol = StockService.normalize_symbol(symbol)

        if not StockService.validate_symbol(symbol):
            return {
                "status": "error",
                "message": "Invalid NSE stock symbol"
            }

        with client.start_session() as session:
            with session.start_transaction():

                StockRepository.upsert_master(symbol)

                # -------- FETCH DATA --------
                if range_value:
                    calculated_start = StockService.calculate_start_from_range(range_value)

                    data = yf.download(
                        symbol,
                        start=calculated_start.strftime("%Y-%m-%d"),
                        interval="1d"
                    )
                else:
                    data = yf.download(symbol, period="1y", interval="1d")

                if data.empty:
                    session.abort_transaction()
                    return {
                        "status": "error",
                        "message": "No price data found"
                    }

                result = StockRepository.bulk_upsert(symbol, data)

                inserted_count = result["inserted"]

                start_date = data.index.min().to_pydatetime()
                end_date = data.index.max().to_pydatetime()

                StockRepository.update_master_metadata(
                    symbol,
                    inserted_count,
                    start_date,
                    end_date
                )

                return {
                    "status": "success",
                    "symbol": symbol,
                    "inserted_documents": inserted_count,
                    "date_range": {
                        "from": start_date,
                        "to": end_date
                    }
                }