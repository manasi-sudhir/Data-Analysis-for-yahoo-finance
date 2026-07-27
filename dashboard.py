"""
Live NVIDIA dashboard.

    streamlit run dashboard.py

Reads from the processed feature tables that the pipeline/scheduler build.
Auto-refreshes on a timer so it stays "live" as long as scheduler.py (or the
"Fetch now" button here) keeps feeding new data into the database.
"""
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src import database
from src.pipeline import run_pipeline

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
st.subheader("Daily Price & Technical Indicators")
if not daily.empty:
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, row_heights=[0.55, 0.2, 0.25],
        vertical_spacing=0.04,
        subplot_titles=("Price + Bollinger Bands + SMA/EMA", "RSI (14)", "MACD"),
    )

    fig.add_trace(go.Candlestick(
        x=daily["date"], open=daily["open"], high=daily["high"],
        low=daily["low"], close=daily["close"], name="OHLC"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["sma_20"], name="SMA 20",
                              line=dict(color="blue", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["sma_50"], name="SMA 50",
                              line=dict(color="purple", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["bb_upper"], name="BB Upper",
                              line=dict(color="gray", width=1, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["bb_lower"], name="BB Lower",
                              line=dict(color="gray", width=1, dash="dot"),
                              fill="tonexty", fillcolor="rgba(128,128,128,0.08)"), row=1, col=1)

    fig.add_trace(go.Scatter(x=daily["date"], y=daily["rsi_14"], name="RSI 14",
                              line=dict(color="teal", width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.add_trace(go.Bar(x=daily["date"], y=daily["macd_hist"], name="MACD Hist",
                          marker_color="lightgray"), row=3, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["macd"], name="MACD",
                              line=dict(color="blue", width=1)), row=3, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["macd_signal"], name="Signal",
                              line=dict(color="orange", width=1)), row=3, col=1)

    fig.update_layout(height=800, xaxis_rangeslider_visible=False,
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
