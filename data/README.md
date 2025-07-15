# Sample Portfolio Files

This directory contains several pre-built portfolio examples to help you get started with the portfolio analysis tool.

## Available Portfolios

### 1. `sample_portfolio.csv` - Balanced Diversified Portfolio
A well-balanced portfolio mixing stocks, commodities, and bonds:
- **Stocks (55%)**: Apple (AAPL), Microsoft (MSFT), Johnson & Johnson (JNJ), Exxon Mobil (XOM)
- **Commodities (30%)**: Gold (GLD), Silver (SLV), Agriculture (DBA)
- **Index Funds (15%)**: Total Stock Market (VTI), Bonds (BND)

### 2. `commodities_portfolio.csv` - Diversified Portfolio with Commodity Exposure
A globally diversified portfolio with one comprehensive commodity ETF:
- **US Stocks (30%)**: S&P 500 ETF (SPY)
- **Commodities (20%)**: Diversified Commodity Strategy ETF (PDBC) - *includes energy, agriculture, and metals*
- **International Stocks (23%)**: Developed Markets (VEA) + Emerging Markets (VWO)
- **Real Estate (12%)**: REITs (VNQ)
- **Bonds (15%)**: Long-term Treasuries (TLT) + Tax-Exempt Bonds (VTEB)

### 3. `commodities_focused.csv` - Pure Commodities Portfolio
A specialized portfolio focused entirely on commodities:
- **Precious Metals (40%)**: Gold (GLD), Silver (SLV)
- **Agriculture (20%)**: Agriculture Fund (DBA)
- **Energy (15%)**: Oil Fund (USO)
- **Diversified Commodities (10%)**: Multi-commodity ETF (PDBC)
- **Industrial Metals (15%)**: Copper Miners (COPX), Rare Earth Metals (REMX)

## How to Use

1. **With the main script**: When you run `python main.py`, choose option 2 and provide the full path to any of these CSV files.

2. **Example path**: 
   ```
   C:\Users\prate\OneDrive\Desktop\Python Projects\portfolio-analysis-tool\data\sample_portfolio.csv
   ```

3. **Custom portfolios**: Use these files as templates to create your own portfolio by editing the tickers and weights.

## CSV Format Requirements

Each CSV file must contain:
- **Ticker column**: Stock/ETF symbols (e.g., AAPL, GLD)
- **Weight column**: Decimal weights that sum to 1.0 (e.g., 0.20 = 20%)
- **Name column**: Optional descriptive names

## Commodity Exposure Explained

### Direct Commodity ETFs:
- **GLD**: Tracks gold bullion prices
- **SLV**: Tracks silver bullion prices
- **USO**: Tracks crude oil futures
- **DBA**: Tracks agricultural commodities (corn, wheat, soybeans, sugar)

### Commodity-Related Stocks:
- **XOM**: Energy sector exposure through Exxon Mobil
- **COPX**: Copper mining companies
- **REMX**: Rare earth and strategic metals mining

### Multi-Commodity ETFs:
- **PDBC**: Diversified commodity futures across energy, agriculture, and metals

These portfolios provide different levels of commodity exposure to help diversify beyond traditional stocks and bonds.
