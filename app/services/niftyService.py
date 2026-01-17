import requests
import pandas as pd
from nselib import capital_market

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
}

URL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"

def get_nifty50_data():
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=HEADERS)

    res = session.get(URL, headers=HEADERS)
    res.raise_for_status()
    data = res.json()

    # First row is Nifty index info
    index_data = data["data"][0]
    nifty = {
        "name": index_data.get("indexSymbol", "NIFTY 50"),
        "last": index_data.get("lastPrice"),
        "open": index_data.get("open"),
        "high": index_data.get("dayHigh"),
        "low": index_data.get("dayLow"),
        "previousClose": index_data.get("previousClose"),
        "percentChange": index_data.get("pChange")
    }

    # Remaining rows are individual stocks
    stocks_list = data["data"][1:]
    stocks_df = pd.DataFrame(stocks_list)

    # Pick only the relevant columns with correct names
    stocks = stocks_df[[
        "symbol", "open", "dayHigh", "dayLow", "lastPrice", "pChange", "totalTradedVolume"
    ]].rename(columns={
        "symbol": "stock",
        "dayHigh": "high",
        "dayLow": "low",
        "lastPrice": "ltp",
        "pChange": "percentChange",
        "totalTradedVolume": "volume"
    })

    return {
        "nifty": nifty,
        "stocks": stocks.to_dict(orient="records"),
        "count": len(stocks)
}


def get_bulk_deals(period: str = "1W"):
    """
    period: 1D | 1W | 1M
    """

    try:
        df = capital_market.bulk_deal_data(period=period)

        # Clean column names (frontend friendly)
        df.columns = [
            col.replace(" ", "_")
               .replace("/", "_")
               .replace(".", "")
            for col in df.columns
        ]

        # Convert dataframe to JSON-safe format
        data = df.fillna("").to_dict(orient="records")

        return {
            "period": period,
            "count": len(data),
            "data": data
        }

    except Exception as e:
        return {
            "error": str(e)
        }

def get_all_indices():
    """
    NSE Market Watch – All Indices
    """
    try:
        df = capital_market.market_watch_all_indices()

        # Clean NaN values for JSON
        df = df.fillna("")

        return {
            "status": "success",
            "count": len(df),
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }











