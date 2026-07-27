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

