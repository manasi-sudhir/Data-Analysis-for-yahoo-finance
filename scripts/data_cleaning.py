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
