import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots 
import make_subplots

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
# Top metric cards
# ---------------------------------------------------------------------------
if not intraday.empty:
    latest = intraday.iloc[-1]
    prev = intraday.iloc[-2] if len(intraday) > 1 else latest

    price_delta = latest["current_price"] - prev["current_price"]
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Current Price", f"${latest['current_price']:.2f}", f"{price_delta:+.2f}")
    col2.metric("Day High", f"${latest['day_high']:.2f}")
    col3.metric("Day Low", f"${latest['day_low']:.2f}")
    col4.metric("Volume", f"{latest['volume']:,.0f}")
    col5.metric("Market Cap", f"${latest['market_cap']/1e12:.2f}T")
    st.caption(f"Last snapshot: {latest['timestamp']}")

st.divider()

# ---------------------------------------------------------------------------
# Intraday chart
# ---------------------------------------------------------------------------
st.subheader("Intraday Price (live snapshots)")
if not intraday.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=intraday["timestamp"], y=intraday["current_price"],
        mode="lines", name="Price", line=dict(color="#76b900", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=intraday["timestamp"], y=intraday["rolling_mean_10"],
        mode="lines", name="Rolling mean (10)", line=dict(color="orange", width=1, dash="dot")
    ))
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10),
                       xaxis_title="Time", yaxis_title="Price (USD)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No intraday snapshots yet.")

st.divider()

# ---------------------------------------------------------------------------
# Daily chart with technical indicators
# ---------------------------------------------------------------------------
st.subheader("Daily Price & Simple Trend Indicators")
if not daily.empty:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, row_heights=[0.65, 0.35],
        vertical_spacing=0.06,
        subplot_titles=("Price + 20/50-Day Moving Averages", "Daily % Return"),
    )

    fig.add_trace(go.Candlestick(
        x=daily["date"], open=daily["open"], high=daily["high"],
        low=daily["low"], close=daily["close"], name="OHLC"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["sma_20"], name="SMA 20",
                              line=dict(color="blue", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["sma_50"], name="SMA 50",
                              line=dict(color="purple", width=1)), row=1, col=1)

    # Daily % return as a simple up/down bar chart - green for up days, red for down days.
    bar_colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in daily["daily_return"].fillna(0)]
    fig.add_trace(go.Bar(x=daily["date"], y=daily["daily_return"], name="Daily Return %",
                          marker_color=bar_colors), row=2, col=1)

    fig.update_layout(height=650, xaxis_rangeslider_visible=False,
                       margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)
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