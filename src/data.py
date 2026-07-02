import os
from datetime import datetime, timedelta, timezone
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.enums import DataFeed
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import Adjustment


def download_ohlcv(ticker: str, years: int = 5) -> pd.DataFrame:
    """Download daily OHLCV bars from Alpaca and return a clean DataFrame."""
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    if not api_key or not secret_key:
        raise ValueError("Missing Alpaca credentials. Put ALPACA_API_KEY and ALPACA_SECRET_KEY in .env or environment variables.")

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=int(years * 365.25) + 30)  # small buffer for indicators

    client = StockHistoricalDataClient(api_key, secret_key)
    request = StockBarsRequest(
        symbol_or_symbols=ticker,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        adjustment="all",
        feed=DataFeed.IEX,
    )   
    bars = client.get_stock_bars(request).df

    if bars.empty:
        raise ValueError(f"No data returned for {ticker}.")

    if isinstance(bars.index, pd.MultiIndex):
        df = bars.xs(ticker.upper(), level=0).copy()
    else:
        df = bars.copy()

    df.index = pd.to_datetime(df.index)
    df = df.rename(columns=str.lower)
    df = df[["open", "high", "low", "close", "volume"]]
    df = df.dropna().sort_index()
    return df
