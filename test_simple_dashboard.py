"""
Simple test dashboard to identify issues
"""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Create simple app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Test Dashboard"

# Simple layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("🚀 Portfolio Analysis Tool - Test", className="text-center mb-4"),
            html.P("If you can see this, the basic Dash setup is working!", className="text-center"),
            html.Hr(),
            html.Div([
                html.H3("Test Components:"),
                dcc.Graph(
                    id='test-chart',
                    figure={
                        'data': [
                            {'x': [1, 2, 3, 4], 'y': [10, 11, 12, 13], 'type': 'scatter', 'name': 'Test'},
                        ],
                        'layout': {
                            'title': 'Test Chart'
                        }
                    }
                )
            ])
        ])
    ])
], fluid=True)

if __name__ == '__main__':
    print("🧪 Starting Test Dashboard on http://127.0.0.1:8055")
    app.run(debug=True, host='127.0.0.1', port=8055)
