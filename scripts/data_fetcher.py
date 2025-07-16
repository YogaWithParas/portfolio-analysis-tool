"""
Data fetching module for portfolio analysis tool.
Handles downloading historical data from Yahoo Finance.
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd


def fetch_data(assets):
    """Fetch historical data for given assets over the last 5 years."""
    import os

    excel_path = os.path.join('data', 'fetched_data.xlsx')
    # You can set desired frequency here: '1d' (daily), '1wk' (weekly), '1mo' (monthly)
    desired_frequency = '1d'  # Change to '1mo' for monthly, '1wk' for weekly, etc.
    def validate_excel(path, assets):
        try:
            df = pd.read_excel(path, index_col=0, parse_dates=True)
            # Check columns
            missing_assets = [a for a in assets if a not in df.columns]
            if missing_assets:
                print(f"Excel file missing assets: {missing_assets}")
                return False
            # Check index type
            if not pd.api.types.is_datetime64_any_dtype(df.index):
                print("Excel file index is not datetime.")
                return False
            # Check for missing values
            if df.isnull().any().any():
                print("Excel file contains missing values.")
                return False
            return True
        except Exception as e:
            print(f"Excel file validation error: {e}")
            return False

    if os.path.exists(excel_path) and validate_excel(excel_path, assets):
        print(f"Reading valid data from {excel_path}")
        all_data = pd.read_excel(excel_path, index_col=0, parse_dates=True)
        if all_data is None or all_data.empty:
            print("Error: Excel file is empty or could not be loaded. Returning empty DataFrame.")
            return pd.DataFrame()
        return all_data.dropna(axis=1)
    else:
        if os.path.exists(excel_path):
            print(f"Excel file {excel_path} is invalid. Re-fetching data.")
        else:
            print(f"Excel file {excel_path} not found. Fetching data.")

    # If file does not exist or is invalid, fetch from Yahoo Finance
    end_date = datetime.today()
    start_date = end_date - timedelta(days=5*365)
    all_data = pd.DataFrame()
    for asset in assets:
        try:
            ticker_data = yf.download(asset, start=start_date, end=end_date, interval=desired_frequency,
                                    auto_adjust=True, progress=False)
            if ticker_data.empty:
                print(f"No data received for {asset}")
                continue
            if isinstance(ticker_data.columns, pd.MultiIndex):
                if ('Adj Close', asset) in ticker_data.columns:
                    data = ticker_data[('Adj Close', asset)]
                elif ('Close', asset) in ticker_data.columns:
                    data = ticker_data[('Close', asset)]
                else:
                    print(f"Could not find price data for {asset}")
                    continue
            elif 'Adj Close' in ticker_data.columns:
                data = ticker_data['Adj Close']
            elif 'Close' in ticker_data.columns:
                data = ticker_data['Close']
            else:
                print(f"Could not find price columns for {asset}")
                continue
            freq = pd.infer_freq(data.index)
            print(f"Frequency for {asset}: {freq}")
            # Confirm if frequency matches desired
            if freq is None:
                print(f"Warning: Could not infer frequency for {asset}. Check data integrity.")
            else:
                if desired_frequency == '1d' and freq not in ['B', 'D']:
                    print(f"Warning: {asset} data is not daily. Detected: {freq}")
                elif desired_frequency == '1mo' and freq != 'M':
                    print(f"Warning: {asset} data is not monthly. Detected: {freq}")
                elif desired_frequency == '1wk' and freq != 'W':
                    print(f"Warning: {asset} data is not weekly. Detected: {freq}")
                elif desired_frequency == '1y' and freq != 'A':
                    print(f"Warning: {asset} data is not yearly. Detected: {freq}")
            if len(data) >= 0.9 * (5 * 252):
                all_data[asset] = data
            else:
                print(f"Insufficient data for {asset}. Excluding from portfolio.")
        except Exception as e:
            print(f"Error fetching data for {asset}: {e}. Excluding from portfolio.")
    if all_data is None or all_data.empty:
        print("Error: No valid data fetched from Yahoo Finance. Returning empty DataFrame.")
        return pd.DataFrame()
    # Save to Excel for future use
    all_data.to_excel(excel_path)
    print(f"Saved fetched data to {excel_path}")
    return all_data.dropna(axis=1)
