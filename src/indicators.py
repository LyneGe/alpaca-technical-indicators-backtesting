import numpy as np
import pandas as pd


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add more than 6 technical indicators across trend, momentum, volatility, and volume."""
    out = df.copy()

    # Trend: SMA, EMA
    out["sma_20"] = out["close"].rolling(20).mean()
    out["sma_50"] = out["close"].rolling(50).mean()
    out["ema_12"] = out["close"].ewm(span=12, adjust=False).mean()
    out["ema_26"] = out["close"].ewm(span=26, adjust=False).mean()

    # Trend: MACD
    out["macd"] = out["ema_12"] - out["ema_26"]
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
    out["macd_hist"] = out["macd"] - out["macd_signal"]

    # Volatility: ATR
    prev_close = out["close"].shift(1)
    tr = pd.concat([
        out["high"] - out["low"],
        (out["high"] - prev_close).abs(),
        (out["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    out["atr_14"] = tr.rolling(14).mean()

    # Trend: ADX
    up_move = out["high"].diff()
    down_move = -out["low"].diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    plus_di = 100 * pd.Series(plus_dm, index=out.index).rolling(14).mean() / out["atr_14"]
    minus_di = 100 * pd.Series(minus_dm, index=out.index).rolling(14).mean() / out["atr_14"]
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    out["adx_14"] = dx.rolling(14).mean()

    # Momentum: RSI
    delta = out["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    out["rsi_14"] = 100 - (100 / (1 + rs))

    # Momentum: Stochastic Oscillator
    low_14 = out["low"].rolling(14).min()
    high_14 = out["high"].rolling(14).max()
    out["stoch_k"] = 100 * (out["close"] - low_14) / (high_14 - low_14)
    out["stoch_d"] = out["stoch_k"].rolling(3).mean()

    # Momentum: Williams %R
    out["williams_r"] = -100 * (high_14 - out["close"]) / (high_14 - low_14)

    # Volatility: Bollinger Bands
    rolling_std = out["close"].rolling(20).std()
    out["bb_mid"] = out["sma_20"]
    out["bb_upper"] = out["bb_mid"] + 2 * rolling_std
    out["bb_lower"] = out["bb_mid"] - 2 * rolling_std

    # Volume: OBV
    direction = np.sign(out["close"].diff()).fillna(0)
    out["obv"] = (direction * out["volume"]).cumsum()
    out["obv_sma_20"] = out["obv"].rolling(20).mean()

    # Volume: Chaikin Money Flow
    mfm_den = (out["high"] - out["low"]).replace(0, np.nan)
    mfm = ((out["close"] - out["low"]) - (out["high"] - out["close"])) / mfm_den
    mfv = mfm * out["volume"]
    out["cmf_20"] = mfv.rolling(20).sum() / out["volume"].rolling(20).sum()

    return out.dropna()
