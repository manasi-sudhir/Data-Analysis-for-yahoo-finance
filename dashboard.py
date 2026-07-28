import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from scripts import database
from scripts.pipeline import run_pipeline

st.set_page_config(page_title="NVIDIA Live Dashboard", page_icon="📈", layout="wide")

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
st.sidebar.title("⚙️ Controls")
refresh_seconds = st.sidebar.slider("Auto-refresh every (seconds)", 10, 120, 30)
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)

if st.sidebar.button("🔄 Fetch now"):
    with st.spinner("Fetching latest data from Yahoo Finance..."):
        run_pipeline()
    st.sidebar.success("Done.")

st.sidebar.caption(
    "For this to stay live between visits, also run `python scheduler.py` "
    "in a separate terminal - it keeps polling even when the dashboard tab "
    "is closed."
)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
database.init_db()
intraday = database.read_table("nvidia_intraday_features")
daily = database.read_table("nvidia_daily_features")

st.title("📈 NVIDIA (NVDA) Live Dashboard")

if intraday.empty and daily.empty:
    st.warning(
        "No data yet. Click **Fetch now** in the sidebar, or run "
        "`python scheduler.py` in a terminal to start collecting data."
    )
    st.stop()

# ---------------------------------------------------------------------------
# "Today at a glance" plain-English summary banner
# ---------------------------------------------------------------------------
if not intraday.empty:
    latest = intraday.iloc[-1]
    prev_close = latest["previous_close"]
    change_dollars = latest["current_price"] - prev_close
    change_pct = (change_dollars / prev_close) * 100 if prev_close else 0

    if change_dollars > 0:
        st.success(
            f"🟢 **NVDA is up ${change_dollars:.2f} ({change_pct:+.2f}%)** "
            f"compared to yesterday's close of ${prev_close:.2f}."
        )
    elif change_dollars < 0:
        st.error(
            f"🔴 **NVDA is down ${abs(change_dollars):.2f} ({change_pct:.2f}%)** "
            f"compared to yesterday's close of ${prev_close:.2f}."
        )
    else:
        st.info("⚪ NVDA is unchanged from yesterday's close.")

# ---------------------------------------------------------------------------
# Top metric cards - dollar AND percent shown together, color-coded by Streamlit
# ---------------------------------------------------------------------------
if not intraday.empty:
    open_delta_dollars = latest["current_price"] - latest["open_price"]
    open_delta_pct = (open_delta_dollars / latest["open_price"] * 100) if latest["open_price"] else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Current Price",
        f"${latest['current_price']:.2f}",
        f"{change_dollars:+.2f} ({change_pct:+.2f}%) vs yesterday",
    )
    col2.metric(
        "Since Market Open",
        f"${latest['open_price']:.2f} → ${latest['current_price']:.2f}",
        f"{open_delta_dollars:+.2f} ({open_delta_pct:+.2f}%)",
    )
    col3.metric("Today's Range", f"${latest['day_low']:.2f} - ${latest['day_high']:.2f}")
    col4.metric("Volume Traded", f"{latest['volume']:,.0f} shares")
    st.caption(f"Last updated: {latest['timestamp']}")

st.divider()

# ---------------------------------------------------------------------------
# Last 10 trading days - plain numbers, color-coded, easiest way to see
# how much the stock moved day to day.
# ---------------------------------------------------------------------------
st.subheader("📅 Last 10 Trading Days - Daily Difference")
st.caption(
    "How much the closing price moved compared to the day before, in both "
    "dollars and percent. Green = closed higher, red = closed lower."
)
if not daily.empty:
    daily_sorted = daily.sort_values("date").copy()
    daily_sorted["$ Change"] = daily_sorted["close"].diff()
    recent = daily_sorted.sort_values("date", ascending=False).head(10).copy()
    recent["% Change"] = recent["daily_return"]

    table = recent[["date", "close", "$ Change", "% Change", "volume"]].rename(
        columns={"date": "Date", "close": "Close Price ($)", "volume": "Volume"}
    )

    def color_updown(val):
        if pd.isna(val):
            return ""
        color = "#2ecc71" if val >= 0 else "#e74c3c"
        return f"color: {color}; font-weight: 600"

    styled = (
        table.style
        .format({
            "Close Price ($)": "${:.2f}",
            "$ Change": "{:+.2f}",
            "% Change": "{:+.2f}%",
            "Volume": "{:,.0f}",
        })
        .map(color_updown, subset=["$ Change", "% Change"])
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Same info as a simple labeled bar chart - dollar change per day.
    bar_colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in recent["$ Change"].fillna(0)]
    fig_bar = go.Figure(go.Bar(
        x=recent["date"], y=recent["$ Change"],
        marker_color=bar_colors,
        text=[f"${v:+.2f}" for v in recent["$ Change"]],
        textposition="outside",
    ))
    fig_bar.update_layout(
        height=320, margin=dict(l=10, r=10, t=20, b=10),
        yaxis_title="Dollar change vs previous day", xaxis_title="",
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No daily history yet - click **Fetch now** to pull it.")

st.divider()

# ---------------------------------------------------------------------------
# Intraday chart
# ---------------------------------------------------------------------------
st.subheader("🕐 Today's Price, Check by Check")
st.caption(
    "The green line is the live price each time it was checked today. "
    "The dotted orange line is the average of the last 10 checks - it "
    "smooths out small jumps so the overall direction is easier to see."
)
if not intraday.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=intraday["timestamp"], y=intraday["current_price"],
        mode="lines", name="Price", line=dict(color="#76b900", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=intraday["timestamp"], y=intraday["rolling_mean_10"],
        mode="lines", name="Recent average (last 10 checks)",
        line=dict(color="orange", width=1, dash="dot")
    ))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10),
                       xaxis_title="Time", yaxis_title="Price (USD)",
                       legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No intraday snapshots yet.")

st.divider()

# ---------------------------------------------------------------------------
# Daily chart with moving averages + daily return
# ---------------------------------------------------------------------------
st.subheader("📊 Price History & Simple Trend")
st.caption(
    "Top: daily candlesticks (green = closed higher than it opened, red = "
    "closed lower) plus two moving averages - the 20-day line reacts faster "
    "to recent prices, the 50-day line shows the slower, longer-term trend. "
    "Bottom: the day-to-day percent change, so you can spot the biggest "
    "up and down days at a glance."
)
if not daily.empty:
    fig2 = make_subplots(
        rows=2, cols=1, shared_xaxes=True, row_heights=[0.65, 0.35],
        vertical_spacing=0.06,
        subplot_titles=("Price + 20/50-Day Moving Averages", "Daily % Return"),
    )

    fig2.add_trace(go.Candlestick(
        x=daily["date"], open=daily["open"], high=daily["high"],
        low=daily["low"], close=daily["close"], name="OHLC"
    ), row=1, col=1)
    fig2.add_trace(go.Scatter(x=daily["date"], y=daily["sma_20"], name="20-day average",
                               line=dict(color="blue", width=1)), row=1, col=1)
    fig2.add_trace(go.Scatter(x=daily["date"], y=daily["sma_50"], name="50-day average",
                               line=dict(color="purple", width=1)), row=1, col=1)

    bar_colors2 = ["#2ecc71" if v >= 0 else "#e74c3c" for v in daily["daily_return"].fillna(0)]
    fig2.add_trace(go.Bar(x=daily["date"], y=daily["daily_return"], name="Daily Return %",
                           marker_color=bar_colors2), row=2, col=1)

    fig2.update_layout(height=650, xaxis_rangeslider_visible=False,
                        margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h"))
    st.plotly_chart(fig2, use_container_width=True)

    # Plain-English trend readout
    last_row = daily.sort_values("date").iloc[-1]
    if pd.notna(last_row["sma_20"]) and pd.notna(last_row["sma_50"]):
        if last_row["sma_20"] > last_row["sma_50"]:
            st.info(
                "📈 The 20-day average is **above** the 50-day average - "
                "recent prices have been trending higher than the longer-term average."
            )
        else:
            st.info(
                "📉 The 20-day average is **below** the 50-day average - "
                "recent prices have been trending lower than the longer-term average."
            )
else:
    st.info("No daily history yet - click **Fetch now** to pull it.")

st.divider()

# ---------------------------------------------------------------------------
# Raw / processed data tables
# ---------------------------------------------------------------------------
with st.expander("🔍 View processed intraday data"):
    st.dataframe(intraday.tail(200).sort_values("timestamp", ascending=False), use_container_width=True)
    st.download_button("Download intraday CSV", intraday.to_csv(index=False), "nvidia_intraday_features.csv")

with st.expander("🔍 View processed daily data"):
    st.dataframe(daily.sort_values("date", ascending=False), use_container_width=True)
    st.download_button("Download daily CSV", daily.to_csv(index=False), "nvidia_daily_features.csv")

# ---------------------------------------------------------------------------
# Auto-refresh
# ---------------------------------------------------------------------------
if auto_refresh:
    time.sleep(refresh_seconds)
    st.rerun()
