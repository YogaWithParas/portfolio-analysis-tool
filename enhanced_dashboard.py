"""
Enhanced Interactive Portfolio Dashboard
=======================================

Improved version with:
- Better error handling
- Performance optimizations
- Enhanced UX features
- Accessibility improvements
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

import dash
from dash import dcc, html, Input, Output, callback_context, State, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from datetime import datetime
import warnings
import base64
import io
import yfinance as yf

# Suppress yfinance warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='yfinance')

from scripts.data_fetcher import fetch_data
from scripts.portfolio_metrics import calculate_portfolio_metrics
from scripts.input_handling import create_sample_portfolio
from scripts.efficient_frontier import (
    calculate_efficient_frontier, 
    find_max_sharpe_portfolio,
    find_min_volatility_portfolio
)

# Initialize the Dash app with enhanced features
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
])
app.title = "Portfolio Analysis Dashboard"

# Enhanced custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --primary-color: #0d6efd;
                --success-color: #198754;
                --warning-color: #ffc107;
                --danger-color: #dc3545;
                --dark-color: #212529;
                --light-color: #f8f9fa;
            }
            
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255,255,255,0.9);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }
            
            .pulse-animation {
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            .click-indicator {
                border: 3px solid var(--primary-color);
                animation: clickPulse 0.3s ease-out;
            }
            
            @keyframes clickPulse {
                0% { transform: scale(1); border-color: var(--primary-color); }
                50% { transform: scale(1.02); border-color: var(--success-color); }
                100% { transform: scale(1); border-color: var(--primary-color); }
            }
            
            .metric-card {
                transition: all 0.3s ease;
                border-left: 4px solid var(--primary-color);
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            
            .status-indicator {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
            }
            
            .status-online { background-color: var(--success-color); }
            .status-loading { background-color: var(--warning-color); animation: pulse 1s infinite; }
            .status-error { background-color: var(--danger-color); }
            
            @media (max-width: 768px) {
                .plotly .main-svg {
                    overflow: visible !important;
                }
                .container-fluid {
                    padding: 10px !important;
                }
                h1 { font-size: 1.5rem !important; }
                h4 { font-size: 1.1rem !important; }
            }
            
            @media print {
                .no-print { display: none !important; }
                .print-break { page-break-after: always; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Global variables with enhanced state management
app_state = {
    'portfolio_data': None,
    'efficient_frontier_results': None,
    'last_updated': None,
    'loading': False,
    'error': None,
    'selected_portfolio': None,
    'price_data': {},  # Store individual asset price data
    'selected_assets': set(),  # Track selected assets for chart
    'uploaded_portfolio': None,
    'all_assets': []  # Store all available assets
}

# Enhanced asset information
asset_names_map = {
    'AAPL': 'Apple Inc. (Technology)',
    'MSFT': 'Microsoft Corp. (Technology)', 
    'JNJ': 'Johnson & Johnson (Healthcare)',
    'GLD': 'SPDR Gold Trust ETF (Commodities)',
    'SLV': 'iShares Silver Trust (Commodities)',
    'DBA': 'Invesco DB Agriculture Fund (Commodities)',
    'XOM': 'Exxon Mobil Corp. (Energy)',
    'VTI': 'Vanguard Total Stock Market ETF (Equity)',
    'BND': 'Vanguard Total Bond Market ETF (Fixed Income)'
}

def load_initial_data():
    """Enhanced data loading with error handling"""
    global app_state
    
    try:
        app_state['loading'] = True
        app_state['error'] = None
        
        # Create sample portfolio
        portfolio_df = create_sample_portfolio()
        assets = portfolio_df['Ticker'].tolist()
        weights = portfolio_df['Weight'].tolist()
        
        # Fetch historical data with retry logic
        historical_data = fetch_data(assets)
        
        if historical_data.empty:
            raise Exception("Failed to fetch market data. Please check your internet connection.")
        
        # Calculate efficient frontier
        app_state['efficient_frontier_results'] = calculate_efficient_frontier(
            historical_data, num_portfolios=1000
        )
        
        # Store current portfolio data
        remaining_assets = historical_data.columns.tolist()
        remaining_weights = [weights[assets.index(asset)] for asset in remaining_assets if asset in assets]
        total_weight = sum(remaining_weights)
        normalized_weights = [w / total_weight for w in remaining_weights]
        
        app_state['portfolio_data'] = {
            'assets': remaining_assets,
            'weights': normalized_weights,
            'metrics': calculate_portfolio_metrics(historical_data, normalized_weights)
        }
        
        # Store individual asset price data for charts
        for asset in remaining_assets:
            if asset in historical_data.columns:
                # Use the already adjusted close price data from historical_data
                asset_price_series = historical_data[asset]
                
                # Create a simple DataFrame with price data - avoid complex fetching that might mix up columns
                asset_data = pd.DataFrame({
                    'Close': asset_price_series,
                    'Open': asset_price_series,   # Use close as approximation for simplicity
                    'High': asset_price_series * 1.01,   # Approximate high as 1% above close
                    'Low': asset_price_series * 0.99,    # Approximate low as 1% below close
                    'Volume': 1000000  # Placeholder volume
                })
                
                app_state['price_data'][asset] = asset_data
                if asset not in app_state['all_assets']:
                    app_state['all_assets'].append(asset)
        
        app_state['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        app_state['loading'] = False
        return True
        
    except Exception as e:
        app_state['error'] = str(e)
        app_state['loading'] = False
        print(f"❌ Error loading data: {e}")
        return False

def create_enhanced_frontier_plot():
    """Enhanced efficient frontier plot with reliable browser compatibility"""
    if app_state['efficient_frontier_results'] is None:
        # Error or loading state
        fig = go.Figure()
        if app_state['error']:
            fig.add_annotation(
                text=f"❌ Error: {app_state['error']}<br>Please refresh to try again",
                xref="paper", yref="paper", x=0.5, y=0.5, 
                showarrow=False, font=dict(size=14, color="red")
            )
        else:
            fig.add_annotation(
                text="📊 Loading portfolio data...<br>This may take a few moments",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=14, color="blue")
            )
        fig.update_layout(
            height=600,
            template="plotly_white",
            xaxis=dict(title="Risk"),
            yaxis=dict(title="Return")
        )
        return fig
    
    results = app_state['efficient_frontier_results']
    fig = go.Figure()
    
    # Simplified efficient frontier points for better compatibility
    fig.add_trace(go.Scatter(
        x=results['risks'],
        y=results['returns'],
        mode='markers',
        marker=dict(
            size=8,
            color=results['sharpe_ratios'],
            colorscale='Viridis',
            colorbar=dict(
                title="Sharpe Ratio",
                thickness=15,
                len=0.7,
                x=-0.15,  # Position colorbar on the left side
                xanchor="left"
            ),
            opacity=0.8,
            line=dict(width=0.5, color='white')
        ),
        text=[f"📈 Return: {r:.1%}<br>📊 Risk: {risk:.1%}<br>⚡ Sharpe: {s:.3f}<br>👆 Click to see portfolio!" 
              for r, risk, s in zip(results['returns'], results['risks'], results['sharpe_ratios'])],
        hovertemplate="%{text}<extra></extra>",
        name="Efficient Frontier",
        customdata=list(range(len(results['returns'])))
    ))
    
    # Enhanced portfolio markers
    if app_state['portfolio_data']:
        portfolio = app_state['portfolio_data']
        fig.add_trace(go.Scatter(
            x=[portfolio['metrics']['Risk (Annualized Std Dev)']],
            y=[portfolio['metrics']['Expected Return (CAGR)']],
            mode='markers',
            marker=dict(size=18, color='red', symbol='star', line=dict(width=2, color='white')),
            name="📍 Your Portfolio",
            text=f"Your Current Portfolio<br>📈 Return: {portfolio['metrics']['Expected Return (CAGR)']:.1%}<br>📊 Risk: {portfolio['metrics']['Risk (Annualized Std Dev)']:.1%}<br>⚡ Sharpe: {portfolio['metrics']['Sharpe Ratio']:.3f}",
            hovertemplate="%{text}<extra></extra>"
        ))
    
    # Optimal portfolios with enhanced styling
    max_sharpe = find_max_sharpe_portfolio(results)
    min_vol = find_min_volatility_portfolio(results)
    
    fig.add_trace(go.Scatter(
        x=[max_sharpe['risk']],
        y=[max_sharpe['return']],
        mode='markers',
        marker=dict(size=15, color='gold', symbol='diamond', line=dict(width=2, color='orange')),
        name="🏆 Max Sharpe",
        text=f"Maximum Sharpe Ratio<br>📈 Return: {max_sharpe['return']:.1%}<br>📊 Risk: {max_sharpe['risk']:.1%}<br>⚡ Sharpe: {max_sharpe['sharpe_ratio']:.3f}",
        hovertemplate="%{text}<extra></extra>"
    ))
    
    fig.add_trace(go.Scatter(
        x=[min_vol['risk']],
        y=[min_vol['return']],
        mode='markers',
        marker=dict(size=15, color='lightblue', symbol='diamond', line=dict(width=2, color='blue')),
        name="🛡️ Min Risk",
        text=f"Minimum Volatility<br>📈 Return: {min_vol['return']:.1%}<br>📊 Risk: {min_vol['risk']:.1%}<br>⚡ Sharpe: {min_vol['sharpe_ratio']:.3f}",
        hovertemplate="%{text}<extra></extra>"
    ))
    
    # Enhanced layout with colorbar on left and legend on right
    fig.update_layout(
        title=dict(
            text="🎯 Interactive Efficient Frontier - Click Any Point!",
            x=0.5,
            xanchor='center',
            font=dict(size=18, family="Arial Black")
        ),
        xaxis=dict(
            title="Risk (Annual Volatility %)",
            tickformat=".1%",
            gridcolor='lightgray',
            gridwidth=1
        ),
        yaxis=dict(
            title="Expected Return (Annual %)",
            tickformat=".1%",
            gridcolor='lightgray',
            gridwidth=1
        ),
        height=600,
        template="plotly_white",
        margin=dict(l=120, r=200, t=100, b=80),  # More space on left for colorbar, less on right
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=1.02,  # Moved legend closer since colorbar is now on left
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1,
            font=dict(size=12),
            itemsizing="constant"
        ),
        autosize=True,
        showlegend=True,
        hovermode='closest'
    )
    
    return fig

def create_enhanced_pie_chart(weights, assets, title="Portfolio Allocation"):
    """Enhanced pie chart with fixed sizing to prevent growing/moving"""
    # Use a professional color palette
    colors = px.colors.qualitative.Set3
    
    fig = px.pie(
        values=weights,
        names=assets,
        title=title,
        color_discrete_sequence=colors
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=11,
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        pull=[0.05 if w == max(weights) else 0 for w in weights]  # Highlight largest allocation
    )
    
    fig.update_layout(
        height=400,  # Fixed height to prevent growing
        width=None,   # Responsive width
        showlegend=False,  # Remove legend to prevent layout issues
        margin=dict(l=20, r=20, t=60, b=20),  # Consistent margins
        template="plotly_white",
        font=dict(family="Arial"),
        autosize=False,  # Prevent auto-resizing
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_status_indicator():
    """Create a status indicator for data freshness"""
    if app_state['loading']:
        return html.Div([
            html.Span(className="status-indicator status-loading"),
            html.Span("Loading data...", className="text-warning")
        ])
    elif app_state['error']:
        return html.Div([
            html.Span(className="status-indicator status-error"),
            html.Span("Connection error", className="text-danger")
        ])
    elif app_state['last_updated']:
        return html.Div([
            html.Span(className="status-indicator status-online"),
            html.Span(f"Last updated: {app_state['last_updated']}", className="text-success small")
        ])
    else:
        return html.Div()

@app.callback(
    Output("legend-container", "style"),
    [Input("close-legend", "n_clicks")]
)
def hide_legend(n_clicks):
    if n_clicks and n_clicks > 0:
        return {"display": "none"}
    return {}

# Enhanced App Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3("How This Tool Works", className="mb-2"),
                dbc.Alert([
                    html.Button("×", id="close-legend", n_clicks=0, style={"float": "right", "fontSize": "1.5rem", "border": "none", "background": "none", "cursor": "pointer"}),
                    html.Ul([
                        html.Li([html.B("Upload Your Data File"), " — Upload your portfolio CSV to start analysis."]),
                        html.Li([html.B("Price Chart of Selected Assets"), " — View price history for assets you select."]),
                        html.Li([html.B("Investment Options Chart"), " — Explore different portfolio options and risk/return tradeoffs."],),
                        html.Li([html.B("Portfolio Breakdown Pie Chart"), " — See how your portfolio is split among assets."]),
                        html.Li([html.B("Portfolio Performance Metrics"), " — Key numbers about your portfolio's performance."]),
                        html.Li([html.B("How Your Money is Split"), " — Table showing allocation for each asset."]),
                        html.Li([html.B("App Status"), " — Shows if the app is ready, loading, or has an error."]),
                        html.Li([html.B("Selected Point Details"), " — Info about the portfolio option you clicked."]),
                    ], className="mb-0")
                ], color="info", className="mb-4", id="legend-alert")
            ], id="legend-container")
        ])
    ]),
    # Enhanced Header with status
    # Enhanced Header with status
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("🚀 Interactive Portfolio Dashboard", className="text-center mb-3"),
                html.Div(id="app-status", className="text-center mb-3"),
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    html.Strong("💡 How to Use: "),
                    "Click on any point in the efficient frontier to analyze that portfolio allocation!"
                ], color="info", className="mb-4")
            ])
        ])
    ]),
    
    # Main Chart with enhanced loading
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-main-chart",
                children=[
                    dcc.Graph(
                        id="investment-options-chart",
                        style={'height': '600px'},
                        config={
                            'responsive': True,
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                            'toImageButtonOptions': {
                                'format': 'png',
                                'filename': 'efficient_frontier',
                                'height': 600,
                                'width': 1000,
                                'scale': 2
                            }
                        }
                    )
                ],
                type="circle",
                color="#0d6efd"
            )
        ], width=12)
    ], className="mb-5"),
    
    # Enhanced Results Section
    dbc.Row([
        # Pie Chart Column
        dbc.Col([
            html.H4([
                html.I(className="fas fa-chart-pie me-2"),
                "Portfolio Breakdown Pie Chart"
            ], className="mb-3"),
            dcc.Loading([
                dcc.Graph(
                    id="portfolio-breakdown-pie",
                    style={'height': '480px'},
                    config={
                        'responsive': True,
                        'displayModeBar': False,
                        'displaylogo': False
                    }
                )
            ])
        ], width=12, lg=6, className="mb-4"),
        
        # Enhanced Metrics Column
        dbc.Col([
            html.H4([
                html.I(className="fas fa-chart-line me-2"),
                "Portfolio Performance Metrics"
            ], className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="performance-metrics")
                ])
            ], className="metric-card h-100")
        ], width=12, lg=6, className="mb-4")
    ], className="mb-5"),
    
    # Enhanced Detailed Table
    dbc.Row([
        dbc.Col([
            html.H4([
                html.I(className="fas fa-table me-2"),
                "How Your Money is Split"
            ], className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="money-split-table", className="table-responsive")
                ])
            ])
        ], width=12)
    ]),
    
    # Hidden div to store click data
    html.Div(id="selected-point-details", style={'display': 'none'}),
    
    # File Upload Section
    dbc.Row([
        dbc.Col([
            html.H4([
                html.I(className="fas fa-upload me-2"),
                "Upload Your Data File"
            ], className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    dcc.Upload(
                        id='upload-file',
                        children=html.Div([
                            html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                            html.Br(),
                            'Drag and Drop or ',
                            html.A('Select CSV File')
                        ], className="text-center"),
                        style={
                            'width': '100%',
                            'height': '120px',
                            'lineHeight': '120px',
                            'borderWidth': '2px',
                            'borderStyle': 'dashed',
                            'borderRadius': '10px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                    ),
                    html.Div(id='upload-status', className="mt-3"),  # (kept same for clarity)
                    html.Small([
                        html.Strong("Expected format: "),
                        "CSV with columns 'Symbol' and 'Weight' (or similar names)"
                    ], className="text-muted")
                ])
            ])
        ], width=12, lg=6),
        
        # Asset Price Chart Section
        dbc.Col([
            html.H4([
                html.I(className="fas fa-chart-area me-2"),
                "Price Chart of Selected Assets"
            ], className="mb-3"),
            dcc.Loading([
                dcc.Graph(
                    id="price-chart",
                    style={'height': '400px'},
                    config={
                        'responsive': True,
                        'displayModeBar': True,
                        'displaylogo': False
                    }
                )
            ])
        ], width=12, lg=6)
    ], className="mb-5"),
    
    # Asset Data Table Section
    dbc.Row([
        dbc.Col([
            html.H4([
                html.I(className="fas fa-database me-2"),
                "Selected Point Details"
            ], className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    html.P([
                        html.I(className="fas fa-info-circle me-2"),
                        "Click the circles to select/deselect assets for the price chart above"
                    ], className="text-info mb-3"),
                    html.Div(id='asset-data-table')  # (kept same for clarity)
                ])
            ])
        ])
    ], className="mb-5")
    
], fluid=True, style={'padding': '20px'})

# Enhanced Callbacks
@app.callback(
    [Output('investment-options-chart', 'figure'),
     Output('app-status', 'children')],
    [Input('investment-options-chart', 'id')]
)
def update_main_plot(_):
    """Initialize main plot with status"""
    return create_enhanced_frontier_plot(), create_status_indicator()

@app.callback(
    [Output('portfolio-breakdown-pie', 'figure'),
     Output('performance-metrics', 'children'),
     Output('money-split-table', 'children'),
     Output('selected-point-details', 'children')],
    [Input('investment-options-chart', 'clickData')],
    [State('selected-point-details', 'children')]
)
def update_portfolio_display(clickData, previous_click):
    """Enhanced portfolio display with click feedback"""
    
    # Default case
    # Defensive: If any required data is missing, return safe defaults
    if (
        clickData is None or
        app_state.get('efficient_frontier_results') is None or
        app_state.get('portfolio_data') is None or
        not app_state['portfolio_data'].get('weights') or
        not app_state['portfolio_data'].get('assets') or
        not app_state['portfolio_data'].get('metrics')
    ):
        return (
            go.Figure().add_annotation(
                text="No portfolio data available.",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=14, color="red")
            ),
            html.Div("No metrics to display."),
            html.Div("No allocation table to display."),
            "default"
        )
    portfolio = app_state['portfolio_data']
    pie_fig = create_enhanced_pie_chart(
        portfolio['weights'],
        portfolio['assets'],
        "Your Current Portfolio"
    )
    metrics = create_enhanced_metrics(portfolio['metrics'], "Current Portfolio")
    table = create_enhanced_table(portfolio['weights'], portfolio['assets'])
    return pie_fig, metrics, table, "default"
    
    # Handle clicks
    # Defensive: Check clickData structure
    try:
        point_index = clickData['points'][0]['pointIndex']
        curve_number = clickData['points'][0].get('curveNumber', 0)
    except Exception:
        return (
            go.Figure().add_annotation(
                text="Invalid selection.",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=14, color="red")
            ),
            html.Div("No metrics to display."),
            html.Div("No allocation table to display."),
            "invalid-click"
        )
    
    if curve_number == 0:  # Efficient frontier click
        results = app_state.get('efficient_frontier_results')
        if not results or not results.get('weights'):
            return (
                go.Figure().add_annotation(
                    text="No efficient frontier data.",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=14, color="red")
                ),
                html.Div("No metrics to display."),
                html.Div("No allocation table to display."),
                "no-frontier"
            )
        try:
            clicked_weights = results['weights'][point_index]
            clicked_return = results['returns'][point_index]
            clicked_risk = results['risks'][point_index]
            clicked_sharpe = results['sharpe_ratios'][point_index]
        except Exception:
            return (
                go.Figure().add_annotation(
                    text="Invalid point selection.",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=14, color="red")
                ),
                html.Div("No metrics to display."),
                html.Div("No allocation table to display."),
                "invalid-point"
            )
        pie_fig = create_enhanced_pie_chart(
            clicked_weights,
            app_state['portfolio_data']['assets'],
            f"Selected Portfolio (Sharpe: {clicked_sharpe:.3f})"
        )
        metrics = create_enhanced_metrics({
            'Expected Return (CAGR)': clicked_return,
            'Risk (Annualized Std Dev)': clicked_risk,
            'Sharpe Ratio': clicked_sharpe
        }, "Selected Portfolio")
        table = create_enhanced_table(clicked_weights, app_state['portfolio_data']['assets'])
        return pie_fig, metrics, table, f"frontier-{point_index}"
    
    # Handle optimal portfolio clicks (Max Sharpe, Min Vol)
    elif curve_number == 2:  # Max Sharpe
        max_sharpe = find_max_sharpe_portfolio(app_state['efficient_frontier_results'])
        return handle_optimal_portfolio(max_sharpe, "Maximum Sharpe Ratio Portfolio")
    
    elif curve_number == 3:  # Min Vol
        min_vol = find_min_volatility_portfolio(app_state['efficient_frontier_results'])
        return handle_optimal_portfolio(min_vol, "Minimum Volatility Portfolio")
    
    # Fallback
    portfolio = app_state['portfolio_data']
    pie_fig = create_enhanced_pie_chart(portfolio['weights'], portfolio['assets'])
    metrics = create_enhanced_metrics(portfolio['metrics'], "Current Portfolio")
    table = create_enhanced_table(portfolio['weights'], portfolio['assets'])
    
    return pie_fig, metrics, table, "fallback"

def handle_optimal_portfolio(optimal_portfolio, title):
    """Handle optimal portfolio display"""
    pie_fig = create_enhanced_pie_chart(
        optimal_portfolio['weights'],
        app_state['portfolio_data']['assets'],
        title
    )
    
    metrics = create_enhanced_metrics({
        'Expected Return (CAGR)': optimal_portfolio['return'],
        'Risk (Annualized Std Dev)': optimal_portfolio['risk'],
        'Sharpe Ratio': optimal_portfolio['sharpe_ratio']
    }, title)
    
    table = create_enhanced_table(
        optimal_portfolio['weights'],
        app_state['portfolio_data']['assets']
    )
    
    return pie_fig, metrics, table, f"optimal-{title.lower().replace(' ', '-')}"

def create_enhanced_metrics(metrics, portfolio_type):
    """Create enhanced metrics display with icons and colors"""
    return dbc.ListGroup([
        dbc.ListGroupItem([
            html.Div([
                html.I(className="fas fa-chart-line text-success me-2"),
                html.Strong("Expected Return: ")
            ], className="d-flex align-items-center"),
            html.Span(f"{metrics['Expected Return (CAGR)']:.2%}", className="badge bg-success")
        ], className="d-flex justify-content-between align-items-center"),
        
        dbc.ListGroupItem([
            html.Div([
                html.I(className="fas fa-exclamation-triangle text-warning me-2"),
                html.Strong("Risk (Volatility): ")
            ], className="d-flex align-items-center"),
            html.Span(f"{metrics['Risk (Annualized Std Dev)']:.2%}", className="badge bg-warning")
        ], className="d-flex justify-content-between align-items-center"),
        
        dbc.ListGroupItem([
            html.Div([
                html.I(className="fas fa-bolt text-primary me-2"),
                html.Strong("Sharpe Ratio: ")
            ], className="d-flex align-items-center"),
            html.Span(f"{metrics['Sharpe Ratio']:.3f}", 
                     className=f"badge bg-{'success' if metrics['Sharpe Ratio'] > 1 else 'info' if metrics['Sharpe Ratio'] > 0.5 else 'secondary'}")
        ], className="d-flex justify-content-between align-items-center")
    ], flush=True)

def create_enhanced_table(weights, assets):
    """Create enhanced allocation table with better formatting"""
    table_data = []
    for asset, weight in zip(assets, weights):
        full_name = asset_names_map.get(asset, asset)
        table_data.append({
            'Ticker': asset,
            'Company/Fund Name': full_name,
            'Weight': f"{weight:.1%}",
            'Weight_Numeric': weight
        })
    
    df = pd.DataFrame(table_data)
    df = df.sort_values('Weight_Numeric', ascending=False)
    df = df.drop('Weight_Numeric', axis=1)
    
    return dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mt-3",
        size="sm"
    )

def parse_uploaded_file(contents, filename):
    """Parse uploaded CSV file for portfolio data"""
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        if 'csv' in filename:
            # Assume CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            # Expected format: Symbol, Weight (or similar names)
            # Try to find the right columns
            symbol_cols = ['Symbol', 'Asset', 'Ticker', 'Stock']
            weight_cols = ['Weight', 'Allocation', 'Percentage', 'Percent']
            
            symbol_col = None
            weight_col = None
            
            for col in df.columns:
                if col in symbol_cols:
                    symbol_col = col
                if col in weight_cols:
                    weight_col = col
            
            if symbol_col is None or weight_col is None:
                # Try first two columns if names don't match
                if len(df.columns) >= 2:
                    symbol_col = df.columns[0]
                    weight_col = df.columns[1]
                else:
                    return None, "Invalid file format. Expected columns: Symbol, Weight"
            
            # Clean and validate data
            df = df[[symbol_col, weight_col]].dropna()
            df[weight_col] = pd.to_numeric(df[weight_col], errors='coerce')
            df = df.dropna()
            
            # Convert percentages if needed (if max weight > 1, assume percentages)
            if df[weight_col].max() > 1:
                df[weight_col] = df[weight_col] / 100
            
            # Normalize weights to sum to 1
            total_weight = df[weight_col].sum()
            if total_weight > 0:
                df[weight_col] = df[weight_col] / total_weight
            
            return df.set_index(symbol_col)[weight_col].to_dict(), None
        
        else:
            return None, "Please upload a CSV file"
            
    except Exception as e:
        return None, f"Error parsing file: {str(e)}"

def create_asset_price_chart():
    """Create interactive asset price chart"""
    if not app_state['price_data'] or not app_state['selected_assets']:
        fig = go.Figure()
        fig.add_annotation(
            text="📈 Select assets from the table below<br>to view their price history",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Asset Price History",
            height=400,
            margin=dict(l=40, r=40, t=60, b=40),
            template="plotly_white"
        )
        return fig
    
    fig = go.Figure()
    
    # Add selected assets to the chart
    colors = px.colors.qualitative.Set1
    color_idx = 0
    
    for asset in app_state['selected_assets']:
        if asset in app_state['price_data']:
            price_data = app_state['price_data'][asset]
            fig.add_trace(go.Scatter(
                x=price_data.index,
                y=price_data['Close'],
                mode='lines',
                name=f"{asset} ({asset_names_map.get(asset, asset)})",
                line=dict(color=colors[color_idx % len(colors)], width=2),
                hovertemplate=f"<b>{asset}</b><br>" +
                             "Date: %{x}<br>" +
                             "Price: $%{y:.2f}<br>" +
                             "<extra></extra>"
            ))
            color_idx += 1
    
    fig.update_layout(
        title=f"📈 Price History - {len(app_state['selected_assets'])} Asset(s) Selected",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_asset_data_table():
    """Create interactive asset data table with selection buttons"""
    if not app_state['price_data']:
        return html.Div([
            html.P("📊 Asset data will appear here after loading portfolio", 
                   className="text-muted text-center")
        ])
    
    # Prepare table data
    table_data = []
    for asset, data in app_state['price_data'].items():
        try:
            # Ensure we're using the Close price, not volume
            if 'Close' in data.columns:
                latest_price = data['Close'].iloc[-1]
                first_price = data['Close'].iloc[0]
            else:
                # Fallback if Close column doesn't exist
                latest_price = data.iloc[-1, 0]  # First column, last row
                first_price = data.iloc[0, 0]   # First column, first row
            
            # Calculate percentage return
            price_change = ((latest_price - first_price) / first_price) * 100
            
            # Debug: Print values to check for issues
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"[{current_time}] Debug - {asset}: Latest=${latest_price:.2f}, First=${first_price:.2f}, Change={price_change:.2f}%")
            
            table_data.append({
                'Asset': asset,
                'Name': asset_names_map.get(asset, asset),
                'Latest Price': f"${latest_price:.2f}",
                'Total Return': f"{price_change:+.2f}%",
                'Data Points': len(data),
                'Date Range': f"{data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}"
            })
        except Exception as e:
            print(f"Error processing data for {asset}: {e}")
            table_data.append({
                'Asset': asset,
                'Name': asset_names_map.get(asset, asset),
                'Latest Price': "Error",
                'Total Return': "Error",
                'Data Points': len(data),
                'Date Range': "Error"
            })
    
    # Create table with action buttons using pattern-matching callbacks
    table_rows = []
    for row in table_data:
        asset = row['Asset']
        is_selected = asset in app_state['selected_assets']
        
        table_rows.append(
            html.Tr([
                html.Td([
                    dbc.Button(
                        "✓" if is_selected else "○",
                        id={'type': 'asset-button', 'index': asset},
                        color="success" if is_selected else "outline-secondary",
                        size="sm",
                        className="me-2"
                    ),
                    html.Strong(asset)
                ]),
                html.Td(row['Name']),
                html.Td(row['Latest Price']),
                html.Td(row['Total Return'], className="text-success" if "+" in row['Total Return'] else "text-danger"),
                html.Td(row['Data Points']),
                html.Td(row['Date Range'], className="small text-muted")
            ])
        )
    
    return dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Asset", style={"width": "15%"}),
                html.Th("Name", style={"width": "25%"}),
                html.Th("Latest Price", style={"width": "12%"}),
                html.Th("Total Return", style={"width": "12%"}),
                html.Th("Data Points", style={"width": "10%"}),
                html.Th("Date Range", style={"width": "26%"})
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, hover=True, responsive=True, className="mt-3")

# New Callbacks for Enhanced Features

@app.callback(
    [Output('upload-status', 'children'),
     Output('asset-data-table', 'children'),
     Output('price-chart', 'figure')],
    [Input('upload-file', 'contents')],
    [State('upload-file', 'filename')]
)
def handle_file_upload(contents, filename):
    """Handle file upload and update asset data"""
    upload_status = ""
    asset_table = create_asset_data_table()
    price_chart = create_asset_price_chart()
    
    if contents is not None:
        portfolio_dict, error = parse_uploaded_file(contents, filename)
        
        if error:
            upload_status = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Upload Error: {error}"
            ], color="danger")
        else:
            # Process uploaded portfolio
            app_state['uploaded_portfolio'] = portfolio_dict
            
            # Fetch data for uploaded assets
            try:
                symbols = list(portfolio_dict.keys())
                print(f"📊 Fetching data for uploaded portfolio: {symbols}")
                
                for symbol in symbols:
                    try:
                        data = fetch_data(symbol)
                        app_state['price_data'][symbol] = data
                        if symbol not in app_state['all_assets']:
                            app_state['all_assets'].append(symbol)
                    except Exception as e:
                        print(f"❌ Error fetching {symbol}: {e}")
                
                upload_status = dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    f"✅ Successfully uploaded portfolio with {len(portfolio_dict)} assets: {', '.join(portfolio_dict.keys())}"
                ], color="success")
                
                asset_table = create_asset_data_table()
                
            except Exception as e:
                upload_status = dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Data fetch error: {str(e)}"
                ], color="warning")
    
    return upload_status, asset_table, price_chart

# Create a single callback to handle all asset button clicks
@app.callback(
    [Output('price-chart', 'figure', allow_duplicate=True),
     Output('asset-data-table', 'children', allow_duplicate=True)],
    [Input({'type': 'asset-button', 'index': dash.ALL}, 'n_clicks')],
    [State({'type': 'asset-button', 'index': dash.ALL}, 'id')],
    prevent_initial_call=True
)
def update_asset_selection(n_clicks_list, button_ids):
    """Handle asset selection button clicks"""
    ctx = callback_context
    if not ctx.triggered:
        return create_asset_price_chart(), create_asset_data_table()
    
    # Find which button was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id != '{}':
        # Parse the button ID to get the asset
        import json
        button_data = json.loads(button_id)
        asset = button_data['index']
        
        # Toggle selection
        if asset in app_state['selected_assets']:
            app_state['selected_assets'].remove(asset)
            print(f"🔸 Deselected asset: {asset}")
        else:
            app_state['selected_assets'].add(asset)
            print(f"🔹 Selected asset: {asset}")
    
    return create_asset_price_chart(), create_asset_data_table()

# Initialize asset data table on startup
@app.callback(
    [Output('asset-data-table', 'children', allow_duplicate=True),
     Output('price-chart', 'figure', allow_duplicate=True)],
    [Input('investment-options-chart', 'id')],
    prevent_initial_call=True
)
def initialize_asset_components(_):
    """Initialize asset components on startup"""
    return create_asset_data_table(), create_asset_price_chart()

# Initialize data on startup
print("🚀 Loading enhanced portfolio dashboard...")
if load_initial_data():
    print("✅ Data loaded successfully!")
else:
    print("❌ Failed to load initial data")

print("🌐 Starting Enhanced Interactive Dashboard...")
print("📊 Open your browser and go to: http://127.0.0.1:8054")
print("💡 Enhanced features: File upload, asset charts, and interactive selection!")

# Start the enhanced dashboard
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8054)
