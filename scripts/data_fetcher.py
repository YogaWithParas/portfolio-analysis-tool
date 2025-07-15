"""
Data fetching module for portfolio analysis tool.
Handles downloading historical data from Yahoo Finance.
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd


def fetch_data(assets):
    """Fetch historical data for given assets over the last 5 years."""
    # Calculate the start and end dates (5 years from today)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=5*365)

    # Initialize an empty DataFrame to store adjusted close prices
    all_data = pd.DataFrame()

    for asset in assets:
        try:
            # Download data with specific settings to avoid rate limiting
            ticker_data = yf.download(asset, start=start_date, end=end_date, 
                                    auto_adjust=True, progress=False)
            
            # Handle different data structures more carefully
            if ticker_data.empty:
                print(f"No data received for {asset}")
                continue
                
            # For multi-level columns (when downloading single asset)
            if isinstance(ticker_data.columns, pd.MultiIndex):
                # Look for Adj Close first, then Close
                if ('Adj Close', asset) in ticker_data.columns:
                    data = ticker_data[('Adj Close', asset)]
                elif ('Close', asset) in ticker_data.columns:
                    data = ticker_data[('Close', asset)]
                else:
                    print(f"Could not find price data for {asset}")
                    continue
            # For single-level columns
            elif 'Adj Close' in ticker_data.columns:
                data = ticker_data['Adj Close']
            elif 'Close' in ticker_data.columns:
                data = ticker_data['Close']
            else:
                print(f"Could not find price columns for {asset}")
                continue
            
            # Check if data is available for at least 4.5 years (~90% of 5 years)
            if len(data) >= 0.9 * (5 * 252):  # 252 trading days per year
                all_data[asset] = data
            else:
                print(f"Insufficient data for {asset}. Excluding from portfolio.")
        except Exception as e:
            print(f"Error fetching data for {asset}: {e}. Excluding from portfolio.")

    return all_data.dropna(axis=1)
