from pymongo import UpdateOne
from datetime import datetime
from app.core.database import stock_prices, stocks_master


class StockRepository:

# This Function is responsible for if Stock Symbol is not present then Create it, else do nothing.
    @staticmethod
    def upsert_master(symbol: str):
        stocks_master.update_one(
            {"symbol": symbol},
            {
                "$setOnInsert": {
                    "symbol": symbol,
                    "type": "index" if symbol.startswith("^") else "stock",
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    @staticmethod
    def get_last_date(symbol: str):
        latest = stock_prices.find_one(
            {"symbol": symbol},
            sort=[("date", -1)]
        )
        return latest["date"] if latest else None


    @staticmethod
    def update_master_metadata(symbol: str, inserted_count: int, start_date, end_date):
        stocks_master.update_one(
            {"symbol": symbol},
            {
                "$set": {
                    "updated_at": datetime.utcnow(),
                    "documents_inserted": inserted_count,
                    "data_start_date": start_date,
                    "data_end_date": end_date
                }
            }
        )

    @staticmethod
    def bulk_upsert(symbol: str, data):
        if data is None or data.empty:
            return 0

        operations = []

        # Ensure columns are flat (fix for MultiIndex issues)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

        has_adj_close = "Adj Close" in data.columns

        for index, row in data.iterrows():
            try:
                adj_close_value = row["Adj Close"] if has_adj_close else row["Close"]

                operations.append(
                    UpdateOne(
                        {
                            "symbol": symbol,
                            "date": index.to_pydatetime()
                        },
                        {
                            "$set": {
                                "symbol": symbol,
                                "date": index.to_pydatetime(),
                                "open": float(row["Open"]),
                                "high": float(row["High"]),
                                "low": float(row["Low"]),
                                "close": float(row["Close"]),
                                "adj_close": float(adj_close_value),
                                "volume": int(row["Volume"]),
                                "updated_at": datetime.utcnow()
                            }
                        },
                        upsert=True
                    )
                )

            except Exception as e:
                print(f"Error processing row {index}: {e}")
                continue

        if operations:
            result = stock_prices.bulk_write(operations)
            return {
                "inserted": result.upserted_count,
                "modified": result.modified_count
            }

        return 0