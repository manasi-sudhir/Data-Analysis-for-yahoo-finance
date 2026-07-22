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
