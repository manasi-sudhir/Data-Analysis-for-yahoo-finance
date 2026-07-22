import numpy as np
import pandas as pd

def clean_intraday(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # Exact duplicate snapshots (same timestamp) - keep the last write
    df = df.drop_duplicates(subset=["timestamp"], keep="last")
    df = df.sort_values("timestamp").reset_index(drop=True)

    numeric_cols = ["current_price", "open_price", "previous_close",
                     "day_high", "day_low", "volume", "market_cap"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# A price snapshot with a non-positive price is bad data, not a real quote
    df = df[df["current_price"] > 0]

    # Small isolated gaps (a null field on an otherwise valid row) get
    # forward-filled; we don't forward-fill current_price itself since that's
    # the value we most want to trust as directly observed
    ffill_cols = ["open_price", "previous_close", "day_high", "day_low", "market_cap", "currency"]
    df[ffill_cols] = df[ffill_cols].ffill()

    # IQR-based outlier flag on current_price (flag, don't silently drop -
    # a genuine 10% single-day move is real news, not noise)
    q1, q3 = df["current_price"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 3 * iqr, q3 + 3 * iqr
    df["is_price_outlier"] = ~df["current_price"].between(lower, upper)

    return df.reset_index(drop=True)

def clean_daily(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.sort_values("date").reset_index(drop=True)

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # A daily bar needs a valid close and non-negative volume to be usable
    df = df.dropna(subset=["close"])
    df = df[df["close"] > 0]
    df["volume"] = df["volume"].clip(lower=0)

    # High must be >= low, and both must bracket open/close - fix obviously
    # swapped high/low (rare yfinance glitch), otherwise leave as-is
    swapped = df["high"] < df["low"]
    df.loc[swapped, ["high", "low"]] = df.loc[swapped, ["low", "high"]].values

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df.reset_index(drop=True)

