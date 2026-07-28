# NVIDIA Stock Data Analysis

## 1. Introduction

This project analyses NVIDIA Corporation (NVDA) stock-market data using Python.

The project fetches current and historical NVIDIA stock data, cleans the collected observations, creates analytical features, stores raw and processed data in SQLite, and presents the results through a Streamlit dashboard.

Python libraries including yfinance, pandas, NumPy, Streamlit, and Plotly are used for data acquisition, preprocessing, feature engineering, analysis, and visualisation.

---

## 2. Project Overview

The project is divided into four major parts:

### 2.1 Data Collection

- NVIDIA (NVDA) stock-market data is fetched using the `yfinance` Python package.
- The pipeline collects live market snapshots.
- The pipeline retrieves daily historical OHLCV data.
- The configured historical period is approximately two years.
- A scheduler automatically runs the data pipeline.
- Live data is fetched approximately every 60 seconds while the scheduler is running.
- Historical daily data is refreshed approximately every six hours.

### 2.2 Data Preprocessing

The project cleans the collected intraday and daily stock data before analysis.

The preprocessing stage:

- Converts timestamps and dates into valid datetime formats.
- Removes invalid timestamps and dates.
- Removes duplicate observations.
- Sorts observations chronologically.
- Converts price, volume, and market values to numeric data types.
- Removes non-positive current and closing prices.
- Clips negative daily volume values to zero.
- Forward-fills selected missing intraday fields.
- Corrects daily records where high and low values are swapped.
- Flags potential intraday price outliers using the IQR method.

### 2.3 Feature Engineering

The project creates analytical features from the cleaned NVIDIA stock data.

For intraday data, the project creates:

- `price_change`
- `pct_change_from_prev_snapshot`
- `pct_change_from_open`
- `rolling_mean_10`
- `day_range_pct`

For daily historical data, the project creates:

- `daily_return`
- `sma_20`
- `sma_50`
- `momentum_10`
- `volume_change_pct`

### 2.4 Data Analysis and Dashboard

The project includes a Streamlit dashboard for analysing the processed NVIDIA stock data.

The dashboard displays:

- Current NVIDIA stock price
- Price change from the previous snapshot
- Day high
- Day low
- Trading volume
- Market capitalisation
- Latest snapshot timestamp
- Intraday price movement
- 10-snapshot rolling mean
- Daily candlestick chart
- 20-day simple moving average
- 50-day simple moving average
- Daily percentage returns
- Processed intraday data
- Processed daily data

The dashboard also provides CSV download options for the processed intraday and daily datasets.

---

# 3. Main Implementation Components

## 3.1 Data Fetching

**File:** `scripts/fetch_data.py`

The data-fetching module retrieves NVIDIA market information using `yfinance`.

It:

- Retrieves a current NVDA market snapshot.
- Retrieves daily historical OHLCV data.
- Organises the retrieved information for processing and database storage.
- Handles unavailable or missing market values during data acquisition.

---

## 3.2 Database Management

**File:** `scripts/database.py`

The database module manages the project's SQLite database.

It:

- Initialises the required database tables.
- Stores live NVIDIA stock snapshots.
- Stores and updates historical daily observations.
- Reads stored data for cleaning and feature engineering.
- Stores processed intraday and daily feature tables.

The SQLite database is stored at:

```text
data/nvidia_stock.db
```

---

## 3.3 Data Cleaning

**File:** `scripts/data_cleaning.py`

The project contains separate cleaning functions for intraday and daily data.

### Intraday Cleaning

The `clean_intraday()` function:

- Converts timestamps to datetime values.
- Removes invalid timestamps.
- Removes duplicate timestamps.
- Sorts observations chronologically.
- Converts market columns to numeric values.
- Removes records with non-positive current prices.
- Forward-fills selected missing market fields.
- Creates an `is_price_outlier` flag using the IQR method.

### Daily Cleaning

The `clean_daily()` function:

- Converts dates to datetime values.
- Removes invalid dates.
- Removes duplicate dates.
- Sorts observations chronologically.
- Converts OHLCV columns to numeric values.
- Removes records without a valid closing price.
- Removes non-positive closing prices.
- Clips negative volume values to zero.
- Corrects records where the high value is lower than the low value.
- Standardises dates to `YYYY-MM-DD`.

---

## 3.4 Feature Engineering

**File:** `scripts/feature_engineering.py`

The project contains separate feature-engineering functions for intraday and daily market data.

### Intraday Features

The `add_intraday_features()` function creates:

- `price_change` – change in price from the previous live snapshot.
- `pct_change_from_prev_snapshot` – percentage change from the previous snapshot.
- `pct_change_from_open` – percentage change from the market opening price.
- `rolling_mean_10` – average current price across the latest 10 snapshots.
- `day_range_pct` – daily high-to-low price range as a percentage of the opening price.

### Daily Features

The `add_daily_features()` function creates:

- `daily_return` – percentage change in closing price from the previous trading day.
- `sma_20` – 20-day simple moving average.
- `sma_50` – 50-day simple moving average.
- `momentum_10` – difference between the current close and the closing price 10 trading days earlier.
- `volume_change_pct` – percentage change in trading volume from the previous trading day.

---

## 3.5 Pipeline Orchestration

**File:** `scripts/pipeline.py`

The pipeline module connects the main stages of the project.

It:

- Initialises the SQLite database.
- Fetches the latest NVIDIA market snapshot.
- Refreshes historical daily data when required.
- Runs the data-cleaning functions.
- Runs feature engineering.
- Stores the processed datasets.
- Records pipeline activity and errors in the log file.

---

## 3.6 Automated Scheduler

**File:** `scheduler.py`

The scheduler automatically executes the NVIDIA data pipeline.

The configured schedule:

- Fetches live stock data approximately every **60 seconds**.
- Refreshes historical daily data approximately every **6 hours**.
- Maintains approximately **2 years** of daily historical data.

The scheduler continues collecting data while the Python process is running.

---

## 3.7 Streamlit Dashboard

**File:** `dashboard.py`

The project includes a Streamlit dashboard named **NVIDIA (NVDA) Live Dashboard**.

The dashboard:

- Provides an auto-refresh control.
- Allows the refresh interval to be selected between 10 and 120 seconds.
- Includes a **Fetch now** button for manually running the pipeline.
- Displays the current price and latest price change.
- Displays day high, day low, volume, and market capitalisation.
- Displays an intraday price line chart.
- Displays the 10-snapshot rolling mean.
- Displays a daily candlestick chart.
- Displays the 20-day and 50-day simple moving averages.
- Displays daily percentage returns.
- Shows processed intraday and daily data tables.
- Allows processed datasets to be downloaded as CSV files.

---

# 4. References

## Generative AI Assistance

OpenAI, **ChatGPT** — Generative AI assistance used for frontend dashboard development and project support.

https://chatgpt.com/share/6a68094f-57ac-83eb-a722-664115997d84

https://chatgpt.com/share/6a68091f-a2a0-83eb-a9d1-5abdf1709221

OpenAI, **ChatGPT** — Generative AI assistance used for feature-engineering ideas.

https://chatgpt.com/share/6a6809b4-66fc-83eb-8dc1-9bf3c52c175c

## Python References

W3Schools, **Python Tutorial**

https://www.w3schools.com/python/

## YouTube References

**Live Data Fetching Tutorial**

https://www.youtube.com/watch?v=oWmWFGP9lOg

**Python / Data Analysis Tutorial**

https://www.youtube.com/watch?v=OQBvSQhkehs
