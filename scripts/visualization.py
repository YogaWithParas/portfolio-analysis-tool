"""
Visualization module for portfolio analysis.
Creates charts and plots for portfolio analysis.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_allocation(weights, assets):
    """Visualize portfolio allocation."""
    plt.figure(figsize=(8, 8))
    plt.pie(weights, labels=assets, autopct='%1.1f%%', startangle=90, 
            colors=plt.cm.Paired(range(len(assets))))
    plt.title("Portfolio Allocation", fontsize=16)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()


def plot_efficient_frontier(results, portfolio_metrics):
    """
    Plot the efficient frontier and highlight the given portfolio.

    Parameters:
        results (dict): Efficient frontier simulation results.
        portfolio_metrics (dict): Metrics of the given portfolio.
    """
    plt.figure(figsize=(12, 8))

    # Scatter plot of the efficient frontier
    scatter = plt.scatter(
        results["risks"], results["returns"], c=results["sharpe_ratios"], 
        cmap="viridis", edgecolors="k", marker="o", alpha=0.6, 
        label="Efficient Frontier"
    )
    plt.colorbar(scatter, label="Sharpe Ratio")

    # Highlight the given portfolio
    plt.scatter(
        portfolio_metrics["Risk (Annualized Std Dev)"],
        portfolio_metrics["Expected Return (CAGR)"],
        color="red", s=150, edgecolors="k", linewidth=2, 
        label="Your Portfolio", zorder=5
    )

    plt.title("Efficient Frontier with Portfolio Highlight", fontsize=16)
    plt.xlabel("Risk (Annualized Std Dev)", fontsize=12)
    plt.ylabel("Return (CAGR)", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_optimal_portfolios(results):
    """
    Plot portfolios on the left-most edge of the efficient frontier.
    
    Parameters:
        results (dict): Efficient frontier simulation results.
    """
    # Find minimum risk portfolios
    min_risk = min(results["risks"])
    threshold = 0.001
    
    optimal_risks = []
    optimal_returns = []
    
    for i, risk in enumerate(results["risks"]):
        if risk - min_risk <= threshold:
            optimal_risks.append(results["risks"][i])
            optimal_returns.append(results["returns"][i])
    
    plt.figure(figsize=(12, 8))
    plt.scatter(
        results["risks"], results["returns"], c="lightgray", alpha=0.5, 
        label="All Portfolios", s=20
    )

    plt.scatter(
        optimal_risks, optimal_returns, c="red", s=80, 
        label="Optimal Portfolios", edgecolors="k", linewidth=1
    )
    
    plt.title("Portfolios on the Left-Most Edge of the Efficient Frontier", fontsize=16)
    plt.xlabel("Risk (Annualized Std Dev)", fontsize=12)
    plt.ylabel("Return (CAGR)", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
