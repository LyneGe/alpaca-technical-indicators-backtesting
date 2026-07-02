import numpy as np
import pandas as pd


def buy_and_hold(df: pd.DataFrame) -> pd.Series:
    return pd.Series(1, index=df.index, name="Buy & Hold")


def trend_following(df: pd.DataFrame) -> pd.Series:
    """Buy when MACD confirms uptrend and ADX shows trend strength; sell when MACD weakens."""
    entry = (df["macd"] > df["macd_signal"]) & (df["adx_14"] > 25) & (df["sma_20"] > df["sma_50"])
    exit_ = (df["macd"] < df["macd_signal"]) | (df["sma_20"] < df["sma_50"])
    return _positions_from_rules(entry, exit_, df.index, "Trend Following")


def mean_reversion(df: pd.DataFrame) -> pd.Series:
    """Buy oversold breakdowns; sell overbought rebounds."""
    entry = (df["rsi_14"] < 30) & (df["close"] < df["bb_lower"])
    exit_ = (df["rsi_14"] > 70) | (df["close"] > df["bb_upper"])
    return _positions_from_rules(entry, exit_, df.index, "Mean Reversion")


def custom_strategy(df: pd.DataFrame) -> pd.Series:
    """
    Custom multi-category strategy:
    - Trend: price above SMA50 and MACD above signal
    - Momentum: RSI between 45 and 70, avoiding extreme overbought
    - Volume: CMF positive and OBV above OBV SMA20
    - Volatility exit: price closes below SMA20 or RSI gets too hot/weak
    """
    entry = (
        (df["close"] > df["sma_50"]) &
        (df["macd"] > df["macd_signal"]) &
        (df["rsi_14"].between(45, 70)) &
        (df["cmf_20"] > 0) &
        (df["obv"] > df["obv_sma_20"])
    )
    exit_ = (
        (df["close"] < df["sma_20"]) |
        (df["macd"] < df["macd_signal"]) |
        (df["rsi_14"] > 78) |
        (df["rsi_14"] < 40)
    )
    return _positions_from_rules(entry, exit_, df.index, "Custom Strategy")


def _positions_from_rules(entry: pd.Series, exit_: pd.Series, index, name: str) -> pd.Series:
    position = []
    holding = 0
    for date in index:
        if holding == 0 and bool(entry.loc[date]):
            holding = 1
        elif holding == 1 and bool(exit_.loc[date]):
            holding = 0
        position.append(holding)
    return pd.Series(position, index=index, name=name).astype(int)
