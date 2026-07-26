import numpy as np
import pandas as pd

def add_intraday_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["price_change"] = df["current_price"].diff()
    df["pct_change_from_prev_snapshot"] = df["current_price"].pct_change() * 100
    df["pct_change_from_open"] = (
        (df["current_price"] - df["open_price"]) / df["open_price"] * 100
    )
    df["rolling_mean_10"] = df["current_price"].rolling(10, min_periods=1).mean()
    df["rolling_std_10"] = df["current_price"].rolling(10, min_periods=1).std()
    df["rolling_mean_30"] = df["current_price"].rolling(30, min_periods=1).mean()
    df["day_range_pct"] = (df["day_high"] - df["day_low"]) / df["open_price"] * 100

    vol_mean = df["volume"].rolling(30, min_periods=1).mean()
    vol_std = df["volume"].rolling(30, min_periods=1).std()
    df["volume_zscore"] = (df["volume"] - vol_mean) / vol_std.replace(0, np.nan)

    return df

def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def add_daily_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    close = df["close"]

    df["daily_return"] = close.pct_change() * 100
    df["log_return"] = np.log(close / close.shift(1))

    df["sma_20"] = close.rolling(20, min_periods=1).mean()
    df["sma_50"] = close.rolling(50, min_periods=1).mean()
    df["ema_12"] = close.ewm(span=12, adjust=False).mean()
    df["ema_26"] = close.ewm(span=26, adjust=False).mean()

    df["macd"] = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    df["rsi_14"] = _rsi(close, 14)

    bb_mid = close.rolling(20, min_periods=1).mean()
    bb_std = close.rolling(20, min_periods=1).std()
    df["bb_mid"] = bb_mid
    df["bb_upper"] = bb_mid + 2 * bb_std
    df["bb_lower"] = bb_mid - 2 * bb_std

    df["volatility_20"] = df["log_return"].rolling(20, min_periods=2).std() * np.sqrt(252)
    df["volume_change_pct"] = df["volume"].pct_change() * 100
    df["momentum_10"] = close - close.shift(10)

    return df

if __name__ == "__main__":
    print("Feature engineering module loaded successfully!")