"""
Portfolio metrics calculation module.
Calculates CAGR, risk, and Sharpe ratio for portfolios.
"""

import numpy as np
import pandas as pd


def calculate_portfolio_metrics(data, weights, risk_free_rate=0.03):
    """Calculate portfolio metrics: CAGR, annualized risk, and Sharpe ratio."""
    # Calculate periodic returns
    returns = data.pct_change().dropna()

    # Calculate CAGR for the portfolio
    initial_values = data.iloc[0, :]
    final_values = data.iloc[-1, :]
    years = len(data) / 252  # Assuming daily data, 252 trading days per year

    cagr = {
        asset: (final_values[asset] / initial_values[asset]) ** (1 / years) - 1
        for asset in data.columns
    }

    # Calculate annualized return for risk (volatility)
    annual_returns = returns.mean() * 252
    annualized_risk = returns.std() * np.sqrt(252)

    # Normalize weights
    normalized_weights = [w / sum(weights) for w in weights]

    # Portfolio metrics
    portfolio_return = np.dot(normalized_weights, list(cagr.values()))  # Use CAGR for return
    cov_matrix = returns.cov() * 252
    portfolio_variance = np.dot(normalized_weights, np.dot(cov_matrix, normalized_weights))
    portfolio_std_dev = np.sqrt(portfolio_variance)

    # Sharpe Ratio
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std_dev

    # Return portfolio metrics
    return {
        "Expected Return (CAGR)": portfolio_return,
        "Risk (Annualized Std Dev)": portfolio_std_dev,
        "Sharpe Ratio": sharpe_ratio
    }
