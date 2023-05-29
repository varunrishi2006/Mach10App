import dash
from dash import dcc, html, Input, Output
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import Booking_Insights, Fare_Analytics, Ancillary_Dashboard

app.layout = html.Div([
    html.Div([
        dcc.Link('Forward Booking Dashboard |', href='/apps/Booking_Insights', style={'fontSize': 20}),
        dcc.Link('Fare Analytics Dashboard |', href='/apps/Fare_Analytics', style={'fontSize': 20}),
        dcc.Link('Ancillary Dashboard', href='/apps/Ancillary_Dashboard ', style={'fontSize': 20}),
    ], className="row"),
    dcc.Location(id='url', refresh=False),
    html.Br(),
    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/Booking_Insights':
        return Booking_Insights.layout
    if pathname == '/apps/Fare_Analytics':
        return Fare_Analytics.layout
    if pathname == '/apps/Ancillary_Dashboard':
        return Ancillary_Dashboard.layout
    else:
        return Ancillary_Dashboard.layout


if __name__ == '__main__':
    app.run_server(debug=False)
