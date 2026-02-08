import requests
import pytz
import pandas as pd
from nselib import capital_market
import nselib
from nsepython import *
import yfinance as yf
from datetime import datetime, time

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
}

URL = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"

IST = pytz.timezone("Asia/Kolkata")

MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)


def is_market_open(now: datetime):
    """Check if current time is during market hours"""
    return MARKET_OPEN <= now.time() <= MARKET_CLOSE


def get_nse_holidays():
    """Fetch NSE holidays as pandas DataFrame"""
    try:
        df = nselib.trading_holiday_calendar()
        df["tradingDate"] = pd.to_datetime(df["tradingDate"]).dt.date
        return df
    except Exception as e:
        print("Error fetching NSE holiday data:", e)
        return pd.DataFrame(columns=["tradingDate", "description"])




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


def get_sensex_data():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^BSESN"

    params = {
        "range": "1d",
        "interval": "1m"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()

    result = r.json()["chart"]["result"][0]
    meta = result["meta"]

    last = meta.get("regularMarketPrice")
    prev_close = meta.get("previousClose")

    return {
        "index": "SENSEX",
        "last": last,
        "change": (last - prev_close) if last and prev_close else None,
        "percentChange": (
            ((last - prev_close) / prev_close) * 100
            if last and prev_close else None
        ),
        "open": meta.get("regularMarketOpen"),
        "high": meta.get("regularMarketDayHigh"),
        "low": meta.get("regularMarketDayLow"),
        "previousClose": prev_close,
        "currency": meta.get("currency"),
        "exchange": meta.get("exchangeName"),
        "marketState": meta.get("marketState"),
        "time": meta.get("regularMarketTime")
    }


def get_india_vix():
    data = nse_get_index_quote("INDIA VIX")

    last = float(data.get("last", 0))
    prev = float(data.get("previousClose", last))
    open_ = float(data.get("open", last))

    change = round(last - prev, 2)
    percent_change = round((change / prev) * 100, 2) if prev else 0

    return {
        "symbol": "INDIA VIX",
        "value": last,                # ✅ number
        "change": change,             # ✅ number
        "percent_change": percent_change,
        "open": open_,
        "high": None,
        "low": None,
        "previous_close": prev
    }

def get_usd_inr_convert():
    """Fetch USD/INR exchange rate"""
    ticker = yf.Ticker("USDINR=X")  # Yahoo Finance USD/INR
    data = ticker.history(period="2d")  # get last 2 days to calculate change

    if data.empty or len(data) < 2:
        return {"status": "error", "message": "USD/INR data unavailable"}

    last = data["Close"].iloc[-1]
    prev_close = data["Close"].iloc[-2]

    points_change = round(last - prev_close, 4)
    percent_change = round((points_change / prev_close) * 100, 2)

    return {
        "status": "success",
        "usd_inr": {
            "name": "USD/INR",
            "last": round(last, 4),
            "pointsChange": points_change,
            "percentChange": percent_change
        }
    }


def calculate_change(last, open_):
    points_change = last - open_
    percent_change = (points_change / open_) * 100 if open_ else 0
    return {"pointsChange": round(points_change, 2), "percentChange": round(percent_change, 2)}

def get_usd_inr():
    """Fetch latest USD to INR conversion rate"""
    usd_inr = yf.Ticker("USDINR=X")
    data = usd_inr.history(period="1d")
    if data.empty:
        return None
    return data["Close"].iloc[-1]

def get_gold_price():
    """Get Gold price in INR per kg (approx from COMEX)"""
    gold = yf.Ticker("GC=F")
    data = gold.history(period="5d")  # 5-day to ensure at least one candle exists

    if data.empty:
        return {"status": "error", "message": "Gold data unavailable"}

    last_usd = data["Close"].iloc[-1]
    open_usd = data["Open"].iloc[-1]

    usd_inr = get_usd_inr()
    if not usd_inr:
        return {"status": "error", "message": "USDINR data unavailable"}

    # Convert USD/oz → INR/kg
    last_inr = (last_usd * usd_inr * 1000) / 31.1035
    open_inr = (open_usd * usd_inr * 1000) / 31.1035

    change = calculate_change(last_inr, open_inr)

    return {
        "status": "success",
        "gold": {
            "name": "GOLD (INR/kg)",
            "last": round(last_inr, 2),
            "pointsChange": change["pointsChange"],
            "percentChange": change["percentChange"]
        }
    }

def get_silver_price():
    """Get Silver price in INR per kg (approx from COMEX)"""
    silver = yf.Ticker("SI=F")
    data = silver.history(period="5d")

    if data.empty:
        return {"status": "error", "message": "Silver data unavailable"}

    last_usd = data["Close"].iloc[-1]
    open_usd = data["Open"].iloc[-1]

    usd_inr = get_usd_inr()
    if not usd_inr:
        return {"status": "error", "message": "USDINR data unavailable"}

    # Convert USD/oz → INR/kg
    last_inr = (last_usd * usd_inr * 1000) / 31.1035
    open_inr = (open_usd * usd_inr * 1000) / 31.1035

    change = calculate_change(last_inr, open_inr)

    return {
        "status": "success",
        "silver": {
            "name": "SILVER (INR/kg)",
            "last": round(last_inr, 2),
            "pointsChange": change["pointsChange"],
            "percentChange": change["percentChange"]
        }
    }


def market_status():
    now = datetime.now(IST)
    today = now.date()

    holidays_df = get_nse_holidays()

    # Check if today is weekend
    is_weekend = today.weekday() >= 5  # Saturday=5, Sunday=6

    # Check if today is a holiday
    holiday_row = holidays_df[holidays_df["tradingDate"] == today]

    if not holiday_row.empty:
        status = "HOLIDAY"
        reason = holiday_row.iloc[0]["description"]
    elif is_weekend:
        status = "CLOSED"
        reason = "Weekend"
    elif is_market_open(now):
        status = "OPEN"
        reason = "Market is open"
    else:
        status = "CLOSED"
        reason = "Market is closed"

    return {
        "date": now.strftime("%d %B %Y"),
        "time": now.strftime("%I:%M:%S %p"),
        "status": status,
        "reason": reason
    }
























