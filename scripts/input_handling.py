"""
Input handling module for portfolio analysis.
Handles CSV file input and portfolio data processing.
"""

import pandas as pd
import yfinance as yf
import os


def get_portfolio_input():
    """
    Automatically process portfolio input from a CSV file.
    Returns a DataFrame with Ticker, Name, and Weight columns.
    Also downloads monthly historical data for the tickers and saves it to a CSV file.
    """
    file_path = input("Enter the path to your CSV file: ").strip()
    try:
        # Read CSV file
        data = pd.read_csv(file_path, header=0)
        print("CSV File Preview:")
        print(data.head())

        # Dynamically identify columns for Ticker and Weight
        ticker_col = None
        weight_col = None

        for col in data.columns:
            if "ticker" in col.lower():
                ticker_col = col
            elif "weight" in col.lower():
                weight_col = col

        if not ticker_col or not weight_col:
            raise KeyError("The CSV file must contain columns for Ticker and Weight.")

        # Extract tickers and weights
        tickers = data[ticker_col].tolist()
        weights = list(map(float, data[weight_col]))

        # Get names if available, otherwise fetch from API
        if 'Name' in data.columns:
            names = data['Name'].tolist()
        else:
            print("Fetching asset names from API...")
            names = []
            for ticker in tickers:
                try:
                    asset = yf.Ticker(ticker)
                    names.append(asset.info.get('shortName', 'Unknown'))
                except Exception:
                    names.append('Unknown')

        # Validate weights
        if not all(w > 0 for w in weights):
            raise ValueError("All weights must be positive numbers.")

        # Normalize weights if they do not sum to 1
        total_weight = sum(weights)
        if total_weight != 1.0:
            weights = [w / total_weight for w in weights]
            print("Weights were normalized to sum to 1.")

        # Download monthly data for each ticker and save to CSV
        print("Downloading monthly historical data for tickers...")
        historical_data = pd.DataFrame()

        for ticker in tickers:
            try:
                ticker_data = yf.download(ticker, interval='1mo', period='5y')
                ticker_data['Ticker'] = ticker
                historical_data = pd.concat([historical_data, ticker_data])
            except Exception as e:
                print(f"Failed to download data for {ticker}: {e}")

        # Save the historical data to the data folder
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        historical_data.to_csv(os.path.join(data_dir, "historical_data.csv"))
        print(f"Historical data saved to {os.path.join(data_dir, 'historical_data.csv')}")

        # Create DataFrame to return
        portfolio_df = pd.DataFrame({
            'Ticker': tickers,
            'Name': names,
            'Weight': weights
        })

    except FileNotFoundError:
        print("Error: The specified file was not found.")
        return get_portfolio_input()
    except KeyError as e:
        print(f"Error: {e}")
        return get_portfolio_input()
    except ValueError as e:
        print(f"Error: {e}")
        return get_portfolio_input()

    return portfolio_df


def create_sample_portfolio():
    """Create a sample portfolio for demonstration purposes."""
    sample_data = {
        'Ticker': ['AAPL', 'MSFT', 'JNJ', 'GLD', 'SLV', 'DBA', 'XOM', 'VTI', 'BND'],
        'Name': ['Apple Inc.', 'Microsoft Corp.', 'Johnson & Johnson', 'SPDR Gold Trust ETF', 
                'iShares Silver Trust', 'Invesco DB Agriculture Fund', 'Exxon Mobil Corp.',
                'Vanguard Total Stock Market ETF', 'Vanguard Total Bond Market ETF'],
        'Weight': [0.20, 0.15, 0.10, 0.15, 0.08, 0.07, 0.10, 0.10, 0.05]
    }
    return pd.DataFrame(sample_data)
