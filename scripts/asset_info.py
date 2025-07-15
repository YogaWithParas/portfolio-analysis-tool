"""
Asset Information Module
========================

Provides full names and descriptions for financial assets.
"""

def get_asset_info():
    """
    Returns a dictionary mapping ticker symbols to full asset names and descriptions.
    """
    return {
        # US Stocks
        'AAPL': 'Apple Inc. (Technology)',
        'MSFT': 'Microsoft Corporation (Technology)',
        'GOOGL': 'Alphabet Inc. Class A (Technology)',
        'AMZN': 'Amazon.com Inc. (E-commerce/Cloud)',
        'TSLA': 'Tesla Inc. (Electric Vehicles)',
        'META': 'Meta Platforms Inc. (Social Media)',
        'NFLX': 'Netflix Inc. (Streaming)',
        'NVDA': 'NVIDIA Corporation (Semiconductors)',
        'JPM': 'JPMorgan Chase & Co. (Banking)',
        'JNJ': 'Johnson & Johnson (Healthcare)',
        'PG': 'Procter & Gamble Co. (Consumer Goods)',
        'UNH': 'UnitedHealth Group Inc. (Healthcare)',
        'HD': 'The Home Depot Inc. (Retail)',
        'V': 'Visa Inc. Class A (Financial Services)',
        'MA': 'Mastercard Inc. Class A (Financial Services)',
        'DIS': 'The Walt Disney Company (Entertainment)',
        'ADBE': 'Adobe Inc. (Software)',
        'CRM': 'Salesforce Inc. (Cloud Software)',
        'INTC': 'Intel Corporation (Semiconductors)',
        'AMD': 'Advanced Micro Devices (Semiconductors)',
        
        # ETFs
        'SPY': 'SPDR S&P 500 ETF Trust (US Large Cap)',
        'QQQ': 'Invesco QQQ Trust ETF (NASDAQ-100)',
        'IWM': 'iShares Russell 2000 ETF (US Small Cap)',
        'EFA': 'iShares MSCI EAFE ETF (International Developed)',
        'EEM': 'iShares MSCI Emerging Markets ETF',
        'VTI': 'Vanguard Total Stock Market ETF',
        'VXUS': 'Vanguard Total International Stock ETF',
        'BND': 'Vanguard Total Bond Market ETF',
        'TLT': 'iShares 20+ Year Treasury Bond ETF',
        'LQD': 'iShares iBoxx Investment Grade Corporate Bond ETF',
        'HYG': 'iShares iBoxx High Yield Corporate Bond ETF',
        'TIPS': 'iShares TIPS Bond ETF (Inflation-Protected)',
        'REI': 'Real Estate Investment Trust ETF',
        'VNQ': 'Vanguard Real Estate Index Fund ETF',
        
        # Commodities
        'GLD': 'SPDR Gold Shares ETF (Gold)',
        'SLV': 'iShares Silver Trust ETF (Silver)',
        'DBA': 'Invesco DB Agriculture Fund ETF',
        'DBC': 'Invesco DB Commodity Index Tracking Fund',
        'USO': 'United States Oil Fund LP ETF (Oil)',
        'UNG': 'United States Natural Gas Fund LP ETF',
        'PDBC': 'Invesco Optimum Yield Diversified Commodity Strategy ETF',
        'IAU': 'iShares Gold Trust ETF (Gold Alternative)',
        'PALL': 'Aberdeen Standard Physical Palladium Shares ETF',
        'PPLT': 'Aberdeen Standard Physical Platinum Shares ETF',
        'CORN': 'Teucrium Corn Fund ETF',
        'WEAT': 'Teucrium Wheat Fund ETF',
        'SOYB': 'Teucrium Soybean Fund ETF',
        
        # International
        'FXI': 'iShares China Large-Cap ETF',
        'EWJ': 'iShares MSCI Japan ETF',
        'EWG': 'iShares MSCI Germany ETF',
        'EWU': 'iShares MSCI United Kingdom ETF',
        'EWZ': 'iShares MSCI Brazil ETF',
        'INDA': 'iShares MSCI India ETF',
        'RSX': 'VanEck Russia ETF',
        'EWT': 'iShares MSCI Taiwan ETF',
        
        # Sector ETFs
        'XLK': 'Technology Select Sector SPDR Fund',
        'XLF': 'Financial Select Sector SPDR Fund',
        'XLV': 'Health Care Select Sector SPDR Fund',
        'XLE': 'Energy Select Sector SPDR Fund',
        'XLI': 'Industrial Select Sector SPDR Fund',
        'XLY': 'Consumer Discretionary Select Sector SPDR Fund',
        'XLP': 'Consumer Staples Select Sector SPDR Fund',
        'XLU': 'Utilities Select Sector SPDR Fund',
        'XLB': 'Materials Select Sector SPDR Fund',
        'XLRE': 'Real Estate Select Sector SPDR Fund',
        
        # Crypto
        'GBTC': 'Grayscale Bitcoin Trust (Bitcoin Exposure)',
        'ETHE': 'Grayscale Ethereum Trust (Ethereum Exposure)',
        
        # Currency
        'UUP': 'Invesco DB US Dollar Index Bullish Fund',
        'FXE': 'Invesco CurrencyShares Euro Trust',
        'FXY': 'Invesco CurrencyShares Japanese Yen Trust',
    }

def get_full_name(ticker):
    """
    Get the full name for a ticker symbol.
    
    Args:
        ticker (str): The ticker symbol
        
    Returns:
        str: Full name or ticker if not found
    """
    asset_info = get_asset_info()
    return asset_info.get(ticker.upper(), ticker)

def get_display_name(ticker):
    """
    Get a display-friendly name for charts and tables.
    
    Args:
        ticker (str): The ticker symbol
        
    Returns:
        str: Display name in format "TICKER - Full Name"
    """
    full_name = get_full_name(ticker)
    if full_name == ticker:
        return ticker
    return f"{ticker} - {full_name}"
