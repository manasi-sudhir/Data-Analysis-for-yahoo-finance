import pandas as pd


def add_intraday_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple features to the intraday (live snapshot) price data.

    Each snapshot is one price check taken during the trading day.
    """
    if df.empty:
        return df

    df = df.copy()

    # Dollar change since the previous snapshot.
    df["price_change"] = df["current_price"].diff()

    # Percent change since the previous snapshot.
    df["pct_change_from_prev_snapshot"] = df["current_price"].pct_change() * 100

    # Percent change since the market opened today.
    df["pct_change_from_open"] = (
        (df["current_price"] - df["open_price"]) / df["open_price"] * 100
    )

    # Average price over the last 10 snapshots - smooths out noise so you
    # can see the short-term trend instead of every small wiggle.
    df["rolling_mean_10"] = df["current_price"].rolling(10, min_periods=1).mean()

    # Today's high-to-low price swing, as a percent of the opening price.
    # A bigger number means a more volatile (choppier) trading day.
    df["day_range_pct"] = (df["day_high"] - df["day_low"]) / df["open_price"] * 100

    return df


def add_daily_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple features to the daily (one row per trading day) price data.
    """
    if df.empty:
        return df

    df = df.copy()
    close = df["close"]

    # Percent change in closing price from the previous trading day.
    df["daily_return"] = close.pct_change() * 100

    # Average closing price over the last 20 / 50 trading days.
    # Moving averages smooth out day-to-day noise so the overall trend
    # (going up, going down, flat) is easier to see. The 50-day average
    # reacts more slowly than the 20-day one.
    df["sma_20"] = close.rolling(20, min_periods=1).mean()
    df["sma_50"] = close.rolling(50, min_periods=1).mean()

    # How much the price has moved over the last 10 trading days
    # (positive = up, negative = down).
    df["momentum_10"] = close - close.shift(10)

    # Percent change in trading volume from the previous day.
    # A big jump can mean unusual news or interest in the stock that day.
    df["volume_change_pct"] = df["volume"].pct_change() * 100

    return df


if __name__ == "__main__":
    print("Feature engineering module loaded successfully!")
