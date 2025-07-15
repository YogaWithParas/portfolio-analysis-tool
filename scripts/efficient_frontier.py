"""
Efficient frontier analysis module.
Calculates and analyzes the efficient frontier for portfolio optimization.

EFFICIENT FRONTIER EXPLANATION:
===============================

The efficient frontier represents the set of optimal portfolios that offer the highest expected return 
for each level of risk, or the lowest risk for each level of expected return.

CALCULATION METHODOLOGY:
========================

1. MONTE CARLO SIMULATION:
   - Generate thousands of random portfolio weight combinations
   - Each portfolio has weights that sum to 1.0 (100%)
   - Weights are randomly distributed across all assets

2. FOR EACH RANDOM PORTFOLIO:
   
   a) EXPECTED RETURN CALCULATION:
      - Calculate daily returns: (Price_today - Price_yesterday) / Price_yesterday
      - Annualize returns: Daily_returns * 252 trading days
      - Portfolio return = Sum(Weight_i × Asset_Return_i)
   
   b) RISK (VOLATILITY) CALCULATION:
      - Calculate covariance matrix of asset returns
      - Annualize covariance: Daily_covariance × 252
      - Portfolio variance = W^T × Σ × W (where W = weights, Σ = covariance matrix)
      - Portfolio risk = √(Portfolio_variance)
   
   c) SHARPE RATIO CALCULATION:
      - Sharpe Ratio = (Portfolio_Return - Risk_Free_Rate) / Portfolio_Risk
      - Measures risk-adjusted return

3. EFFICIENT FRONTIER IDENTIFICATION:
   - Plot all portfolios on Risk (x-axis) vs Return (y-axis) graph
   - Color-code by Sharpe ratio to identify best risk-adjusted returns
   - The "efficient frontier" is the upper-left boundary curve
   - Points on this curve are mathematically optimal

4. OPTIMAL PORTFOLIO IDENTIFICATION:
   - Maximum Sharpe Ratio: Best risk-adjusted return
   - Minimum Volatility: Lowest risk portfolio
   - Custom target return: Find minimum risk for desired return level

MATHEMATICAL FORMULAS:
======================

Portfolio Return: Rp = Σ(wi × Ri)
Portfolio Variance: σp² = Σ Σ (wi × wj × σij)
Portfolio Risk: σp = √(σp²)
Sharpe Ratio: SR = (Rp - Rf) / σp

Where:
- wi, wj = weights of assets i and j
- Ri = expected return of asset i
- σij = covariance between assets i and j
- Rf = risk-free rate

WHY IT WORKS:
============ =
- Diversification reduces risk without proportionally reducing return
- Different assets have different risk-return profiles
- Optimal combinations exist that maximize return per unit of risk
- The frontier shows the mathematical limit of portfolio efficiency
"""

import numpy as np
import pandas as pd


def calculate_efficient_frontier(data, num_portfolios=10000, risk_free_rate=0.03):
    """
    Calculate the efficient frontier by simulating a large number of portfolios.

    Parameters:
        data (DataFrame): Historical price data for assets.
        num_portfolios (int): Number of simulated portfolios.
        risk_free_rate (float): Risk-free rate for calculating Sharpe ratio.

    Returns:
        dict: Contains portfolio returns, risks, weights, and Sharpe ratios.
    """
    # Calculate periodic returns
    returns = data.pct_change().dropna()

    # Calculate annualized return and covariance matrix (assuming daily data)
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252

    num_assets = len(mean_returns)
    results = {
        "returns": [],
        "risks": [],
        "sharpe_ratios": [],
        "weights": []
    }

    for _ in range(num_portfolios):
        # Random weights
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)

        # Portfolio metrics
        portfolio_return = np.dot(weights, mean_returns)
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk

        # Append results
        results["returns"].append(portfolio_return)
        results["risks"].append(portfolio_risk)
        results["sharpe_ratios"].append(sharpe_ratio)
        results["weights"].append(weights)

    return results


def suggest_optimal_weights(results):
    """
    Identify and return all portfolios on the left-most edge of the efficient frontier.

    Parameters:
        results (dict): Efficient frontier simulation results.

    Returns:
        list: A list of optimal portfolios with their weights, risks, and returns.
    """
    # Find all portfolios on the efficient frontier's left-most edge
    optimal_portfolios = []
    min_risk = min(results["risks"])
    threshold = 0.001  # Define a threshold to include portfolios close to the left-most edge

    for i, risk in enumerate(results["risks"]):
        if risk - min_risk <= threshold:  # Include portfolios within the threshold of the minimum risk
            optimal_portfolios.append({
                "index": i,
                "weights": results["weights"][i],
                "risk": results["risks"][i],
                "return": results["returns"][i]
            })

    # Print the details of the optimal portfolios
    print("\nOptimal Portfolios on the Left-Most Edge:")
    for portfolio in optimal_portfolios:
        print(
            f"Index: {portfolio['index']}, Risk: {portfolio['risk']:.4f}, "
            f"Return: {portfolio['return']:.4f}, Weights: {portfolio['weights']}"
        )

    return optimal_portfolios


def find_max_sharpe_portfolio(results):
    """
    Find the portfolio with the maximum Sharpe ratio.
    
    Parameters:
        results (dict): Efficient frontier simulation results.
        
    Returns:
        dict: Portfolio with maximum Sharpe ratio.
    """
    max_sharpe_idx = np.argmax(results["sharpe_ratios"])
    
    return {
        "weights": results["weights"][max_sharpe_idx],
        "return": results["returns"][max_sharpe_idx],
        "risk": results["risks"][max_sharpe_idx],
        "sharpe_ratio": results["sharpe_ratios"][max_sharpe_idx]
    }


def find_min_volatility_portfolio(results):
    """
    Find the portfolio with minimum volatility.
    
    Parameters:
        results (dict): Efficient frontier simulation results.
        
    Returns:
        dict: Portfolio with minimum volatility.
    """
    min_vol_idx = np.argmin(results["risks"])
    
    return {
        "weights": results["weights"][min_vol_idx],
        "return": results["returns"][min_vol_idx],
        "risk": results["risks"][min_vol_idx],
        "sharpe_ratio": results["sharpe_ratios"][min_vol_idx]
    }
