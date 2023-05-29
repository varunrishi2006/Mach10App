import dash
import json
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
from pandas.api.types import CategoricalDtype
import datetime
from datetime import datetime as dt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pathlib
from app import app
import dash_auth

# app = dash.Dash(
#     __name__,
#     meta_tags=[{"name": "viewport",
#                 "content": "width=device-width, initial-scale=1"}],
# )
# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

auth = dash_auth.BasicAuth(
    app,
    {'Mach10': 'Mach10@2023'}
)

app.title = "MACH10 Analytics Dashboard"

df_route_data = pd.read_excel(DATA_PATH.joinpath("ancillary.xlsx"), sheet_name='Route_Data')
df_network_data = pd.read_excel(DATA_PATH.joinpath("ancillary.xlsx"), sheet_name='Network_Data')
df_anc_dtd_data = pd.read_excel(DATA_PATH.joinpath("ancillary.xlsx"), sheet_name='anc_bkg_dtd')
anc_seat_trend = pd.read_excel(DATA_PATH.joinpath("ancillary.xlsx"), sheet_name="seat_map_trend")
anc_dist_chan = pd.read_excel(DATA_PATH.joinpath("ancillary.xlsx"), sheet_name="anc_dist_prod")
anc_bkg_prod = pd.read_excel(DATA_PATH.joinpath("ancillary.xlsx"), sheet_name="anc_bkg_prod")
df_anc_prod_data = pd.read_excel(DATA_PATH.joinpath("ancillary.xlsx"), sheet_name='anc_prod_data')

month_order = CategoricalDtype([
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
    'Jan',
    'Feb',
    'Mar'
], ordered=True)

dtd_interval = CategoricalDtype([
    '0-3',
    '4-7',
    '8-15',
    '16-30',
    '31-60',
    '61-90',
    '>90'
], ordered=True)

bkg_prod_order = CategoricalDtype([
    'Retail',
    'Corporate',
    'SME',
    'Family',
    'Sale'
], ordered=True)

anc_prod_order = CategoricalDtype([
    'Seat',
    'Meal',
    'Baggage',
    'Chg/Canc.',
    'Prior Checkin',
    'Travel Ins.',
    'Infant'
], ordered=True)

bkg_chan_order = CategoricalDtype([
    'Web/App',
    'OTAs',
    'B&M TAs',
    'Airport',
    'In-flight'
], ordered=True)

df_anc_prod_data['Rev Contr'] = df_anc_prod_data['Rev/Pax'] / sum(df_anc_prod_data['Rev/Pax'])

anc_bkg_prod['Ancillary Product'] = anc_bkg_prod['Ancillary Product'].astype(anc_prod_order)
anc_bkg_prod['Booking Product'] = anc_bkg_prod['Booking Product'].astype(bkg_prod_order)
anc_dist_chan['Ancillary Product'] = anc_dist_chan['Ancillary Product'].astype(anc_prod_order)
anc_dist_chan['Channel'] = anc_dist_chan['Channel'].astype(bkg_chan_order)
anc_dist_chan['Booking Channel'] = anc_dist_chan['Booking Channel'].astype(bkg_chan_order)

df_route_data['Departure Month'] = df_route_data['Departure Month'].astype(month_order)

df_anc_dtd_data['Ancillary Purchase DTD Range'] = df_anc_dtd_data['Ancillary Purchase DTD Range'].astype(dtd_interval)
df_anc_dtd_data['Booking DTD Range'] = df_anc_dtd_data['Booking DTD Range'].astype(dtd_interval)

list_fy = list(df_route_data['Financial Year'].unique())
list_dy = list(df_route_data['Departure Year'].unique())
list_routes = list(df_route_data['Route'].unique())
list_flights = list(df_route_data['Flight Number'].unique())
list_stage_length = list(df_network_data['Distance Category'].unique())

df_seat_tr = anc_seat_trend[['Rows', 'Column', 'Seat_TR', 'Meal_TR', 'Baggage_TR', 'Change/Cancellation_TR',
                             'Priority Checkin_TR', 'Travel Insurance_TR', 'Infant_TR']]

df_tr = pd.melt(df_seat_tr,
                id_vars=['Rows', 'Column'],
                value_vars=['Seat_TR', 'Meal_TR', 'Baggage_TR', 'Change/Cancellation_TR',
                            'Priority Checkin_TR', 'Travel Insurance_TR', 'Infant_TR'],
                var_name='Product',
                value_name='Take Rate')

df_tr['Product'] = df_tr['Product'].map(lambda x: x[:-3])

df_seat_rpp = anc_seat_trend[['Rows', 'Column', 'Seat_RPP',
                              'Meal_RPP', 'Baggage_RPP', 'Change/Cancellation_RPP',
                              'Priority Checkin_RPP', 'Travel Insurance_RPP', 'Infant_RPP']]

df_rpp = pd.melt(df_seat_rpp,
                 id_vars=['Rows', 'Column'],
                 value_vars=['Seat_RPP', 'Meal_RPP', 'Baggage_RPP', 'Change/Cancellation_RPP',
                             'Priority Checkin_RPP', 'Travel Insurance_RPP', 'Infant_RPP'],
                 var_name='Product',
                 value_name='Rev/Pax')

df_rpp['Product'] = df_rpp['Product'].map(lambda x: x[:-4])

df_seat_rask = anc_seat_trend[['Rows', 'Column', 'Seat_RASK', 'Meal_RASK', 'Baggage_RASK', 'Change/Cancellation_RASK',
                               'Priority Checkin_RASK', 'Travel Insurance_RASK', 'Infant_RASK']]

df_rask = pd.melt(df_seat_rask,
                  id_vars=['Rows', 'Column'],
                  value_vars=['Seat_RASK', 'Meal_RASK', 'Baggage_RASK', 'Change/Cancellation_RASK',
                              'Priority Checkin_RASK',
                              'Travel Insurance_RASK', 'Infant_RASK'],
                  var_name='Product',
                  value_name='RASK')

df_rask['Product'] = df_rask['Product'].map(lambda x: x[:-5])


def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Ancillary Insights",
                    style={"font-weight": "bold"}),
            html.H3("Welcome to the Ancillary Insights Analytics Dashboard"),
            html.P(
                "Explore insights related to Ancillary products like seat selection, meals, baggage, change & cancellations etc. across routes, flights, journey type etc.\n"
                "This dashboard is at route level which could be further drilled down till respective flight numbers by Financial Year.",
                style={'fontSize': 14}),
            html.P(),
            html.Span(children=[
                # html.I("Note: The dashboard has been created considering"),
                html.B("Assumptions: "),
                html.Br(),
                html.I("* Capacity was constant for a route throughout the years."),
                html.Br(),
                html.I(
                    "* Attach rate is defined as total no. of ancillary products sold as a % of total pax booked on the flight")],
                style={'color': 'brown', 'fontSize': 14})
        ],
    )


def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P(),
            html.P("Select Financial Year"),
            dcc.Dropdown(
                id="year-financial",
                options=[{"label": i, "value": i} for i in list_fy],
                value=list_fy[:],
                multi=True,
                className="dcc_control",
            ),
            html.Br(),
            html.P(),
            html.P("Select Stage Length (km)"),
            dcc.Dropdown(
                id="distance-select",
                options=[{"label": i, "value": i} for i in list_stage_length],
                value=list_stage_length[:],
                multi=True,
                className="dcc_control",
            ),
            html.Br(),
            html.P(),
            html.P("Select Route"),
            dcc.Dropdown(
                id="market-select",
                options=[{"label": i, "value": i} for i in list_routes],
                value=list_routes[:],
                multi=True,
                className="dcc_control",
            ),
            html.Br(),
            html.P(),
            html.P("Select Flight"),
            dcc.Dropdown(
                id="flight-select",
                options=[{"label": i, "value": i} for i in list_flights],
                value=list_flights[:],
                multi=True,
                className="dcc_control",
            ),
            # html.Br(),
            # html.Div(
            #     id="reset-btn-outer",
            #     children=html.Button(id="reset-btn", children="Reset", n_clicks=0),
            #     style={"display": "none"}
            # ),
        ],
    )


def calc_filtered_data(fy, route, flight):
    df_int_data = df_route_data[(df_route_data['Financial Year'].isin(fy)) &
                                (df_route_data['Route'].isin(route)) &
                                (df_route_data['Flight Number'].isin(flight))]
    return df_int_data


layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src="/assets/logo_1.png", style={'width': '250', 'height': '70px'})],
        ),
        html.Div(
            [
                html.Div(
                    id="left-column",
                    className="pretty_container four columns",
                    children=[description_card(), generate_control_card()],
                    style={'border': '1px solid black'}
                ),
                # Right column
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H5(id="anc_revText"), html.P("Total Ancillary Revenue")],
                                    id="anc_rev",
                                    className="mini_container",
                                    style={'padding': '4px 12px',
                                           'textAlign': 'center',
                                           'fontWeight': 'bold',
                                           'backgroundColor': 'lightgrey'}
                                ),
                                html.Div(
                                    [html.H5(id="anc_mkt_highText"), html.P("Top-Performing Market")],
                                    id="anc_mkt_high",
                                    className="mini_container",
                                    style={'padding': '4px 8px',
                                           'textAlign': 'center',
                                           'fontWeight': 'bold',
                                           'backgroundColor': 'lightgrey'}
                                ),
                                html.Div(
                                    [html.H5(id="anc_mkt_lowText"), html.P("Under-Performing Market")],
                                    id="anc_mkt_low",
                                    className="mini_container",
                                    style={'padding': '4px 6px', 'textAlign': 'center', 'fontWeight': 'bold',
                                           'backgroundColor': 'lightgrey'}
                                ),
                                html.Div(
                                    [html.H5(id="max_anc_raskText"), html.P("Best Ancillary RASK")],
                                    id="max_anc_rask",
                                    className="mini_container",
                                    style={'padding': '4px 10px', 'textAlign': 'center', 'fontWeight': 'bold',
                                           'backgroundColor': 'lightgrey'}

                                ),
                                html.Div(
                                    [html.H5(id="best_anc_prodText"), html.P("Top-Performing Product")],
                                    id="best_anc_prod",
                                    className="mini_container",
                                    style={'padding': '4px 5px', 'textAlign': 'center', 'fontWeight': 'bold',
                                           'backgroundColor': 'lightgrey'}
                                ),
                                html.Div(
                                    [html.H5(id="crit_anc_prodText"), html.P("Under-Performing Product")],
                                    id="crit_anc_prod",
                                    className="mini_container",
                                    style={'padding': '4px 6px', 'textAlign': 'center', 'fontWeight': 'bold',
                                           'backgroundColor': 'lightgrey'}
                                ),
                                # html.Div(
                                #     [html.H5(id="pref_dtd_rangeText"), html.P("Most Preferred DTD Range")],
                                #     id="pref_dtd_range",
                                #     className="mini_container",
                                #     style={'padding': '0px 10px', 'textAlign': 'center', 'fontWeight': 'bold',
                                #            'backgroundColor': 'lightgrey'}
                                # )
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        # Total Departure Heatmap
                        html.Div(
                            id="anc_rev_card",
                            children=
                            [
                                # html.B("1. Ancillary Performance by Route",
                                #        style={'textAlign': 'center', 'font': 'Arial', 'fontSize': 15}),
                                # html.Br(),
                                # html.P(),
                                dcc.Graph(id="anc_rev_route")
                            ],
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Br(),
        html.Div(
            [
                html.B("2. Ancillary Product Performance",
                       style={'textAlign': 'center', 'font': 'Arial', 'fontSize': 15}),

            ]),
        html.Div(
            [
                html.Div(
                    [
                        html.B("Select Performance Measure :",
                               style={'textAlign': 'center', 'font': 'Arial', 'fontSize': 15}),
                        dcc.RadioItems(
                            id='anc_kpi_radio_1',
                            options=
                            [
                                {'value': 'take_up_rate', 'label': 'Take Rate %'},
                                {'value': 'rev_per_pax', 'label': 'Revenue Per Pax'},
                                {'value': 'anc_rask', 'label': 'Ancillary RASK'}
                            ],
                            value='take_up_rate',
                            inline=True,
                            inputStyle={'margin-right': '10px'},
                            labelStyle={'display': 'inline-block', 'padding': '0.5rem 0.5rem'}
                        ),
                        # dcc.Graph(id="anc_seat_map_2")
                    ],
                    className="pretty_container twelve columns"
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [
                        # html.B("Channel Performance(Current vs Reference Period)"),
                        dcc.Graph(id="product_perf")
                    ],
                    className="pretty_container six columns"
                ),
                html.Div(
                    [
                        # html.B("Inventory Performance(Current vs Reference Period)"),
                        dcc.Graph(id="sub_product_perf")
                    ],
                    className="pretty_container six columns"
                ),
            ],
            className="row flex-display",
        ),

        html.Div(
            [
                html.Div(
                    [
                        # html.B("Ancillary Product Performance by Days-to-Departure"),
                        dcc.Graph(id="anc_bkg_prod_trend")
                    ],
                    className="pretty_container six columns"
                ),
                html.Div(
                    [
                        # html.B("Channel Performance by Days-to-Departure"),
                        dcc.Graph(id="anc_bkg_channel_trend")
                    ],
                    className="pretty_container six columns"
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [
                        # html.B("Ancillary Product Performance by Days-to-Departure"),
                        dcc.Graph(id="anc_seat_map")
                    ],
                    className="pretty_container six columns"
                ),
                html.Div(
                    [
                        # html.B("Channel Performance by Days-to-Departure"),
                        dcc.Graph(id="anc_seat_map_1")
                    ],
                    className="pretty_container six columns"
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.B("3. Ancillary Performance by Seat Map",
                               style={'textAlign': 'center', 'font': 'Arial', 'fontSize': 15}),
                        html.Br(),
                        html.P(),
                        html.B("Select Performance Measure :",
                               style={'textAlign': 'center', 'font': 'Arial', 'fontSize': 13}),
                        dcc.RadioItems(
                            id='anc_kpi_radio',
                            options=
                            [
                                {'value': 'take_up_rate', 'label': 'Take Rate %'},
                                {'value': 'rev_per_pax', 'label': 'Revenue Per Pax'},
                                {'value': 'anc_rask', 'label': 'Ancillary RASK'}
                            ],
                            value='take_up_rate',
                            inline=True,
                            inputStyle={'margin-right': '10px'},
                            labelStyle={'display': 'inline-block', 'padding': '0.5rem 0.5rem'}
                        ),
                        # html.Br(),
                        html.B("Select Ancillary Product :",
                               style={'textAlign': 'center', 'font': 'Arial', 'fontSize': 13}),
                        dcc.Checklist(
                            id='product-checkbox',
                            options=[
                                {'label': 'Seat', 'value': 'Seat'},
                                {'label': 'Meal', 'value': 'Meal'},
                                {'label': 'Baggage', 'value': 'Baggage'},
                                {'label': 'Chg/Canc', 'value': 'Chg/Canc'},
                                {'label': 'Priority Checkin', 'value': 'Prior Checkin'},
                                {'label': 'Travel Insurance', 'value': 'Travel Ins'},
                                {'label': 'Infant', 'value': 'Infant'},
                            ],
                            value=['Seat', 'Meal', 'Baggage', 'Chg/Canc', 'Prior Checkin', 'Travel Ins', 'Infant'],
                            # Initial selected values
                            labelStyle={'display': 'inline', 'margin': '7px'}  # Display checkboxes horizontally
                        ),
                        html.P(),
                        dcc.Graph(id="anc_seat_map_2")
                    ],
                    className="pretty_container twelve columns"
                ),
            ],
            className="row flex-display",
        ),

    ]
)


@app.callback(
    [
        Output("anc_revText", "children"),
        Output("anc_mkt_highText", "children"),
        Output("anc_mkt_lowText", "children"),
        Output("max_anc_raskText", "children"),
        Output("best_anc_prodText", "children"),
        Output("crit_anc_prodText", "children"),
        # Output("pref_dtd_rangeText", "children"),
    ],
    [
        Input("year-financial", "value"),
        Input("market-select", "value"),
        Input("flight-select", "value")
    ]
)
def update_headers(fy, route, flight):
    df_int_data = calc_filtered_data(fy, route, flight)
    # Logic for calculating the total ancillary revenue for a given financial year
    tot_anc_rev = round(df_int_data['Ancillary Revenue (mn)'].sum())
    tot_rev = str(tot_anc_rev) + "mn (USD)"
    # Logic for identifying the market with the highest Ancillary Revenue and its contribution to the total ancillary revenue
    df_int_1 = df_int_data.groupby('Route')['Ancillary Revenue (mn)'].sum()
    mkt_high_rev = df_int_1.idxmax()
    mkt_high_rev_perc = round(df_int_1.max() / tot_anc_rev * 100)
    mkt_high_contr = mkt_high_rev + "(" + str(mkt_high_rev_perc) + str("%)")
    # Logic for identifying the market with the lowest Ancillary Revenue and its contribution to the total ancillary revenue
    mkt_low_rev = df_int_1.idxmin()
    mkt_low_rev_perc = round(df_int_1.min() / tot_anc_rev * 100)
    mkt_low_contr = mkt_low_rev + "(" + str(mkt_low_rev_perc) + str("%)")
    # Logic for identifying the market with the highest Ancillary rask
    df_int_2 = df_route_data.groupby('Route')['Ancillary RASK'].mean()
    mkt_high_rask = df_int_2.idxmax()
    mkt_high_rask_contr = mkt_high_rask + "(" + str(round(df_int_2.min(), 2)) + str(")")
    # Logic for identifying the best ancillary product
    anc_product_best = "Baggage"
    # Logic for worst performing ancillary product
    anc_product_worst = "Infant"
    # Logic for identifying the DTD range for most ancillary product booking
    dtd_most_booked = "31-60"

    return tot_rev, mkt_high_contr, mkt_low_contr, mkt_high_rask_contr, anc_product_best, anc_product_worst


@app.callback(
    Output("anc_rev_route", "figure"),
    [Input("year-financial", "value"),
     Input("market-select", "value"),
     Input("distance-select", 'value'),
     Input("flight-select", "value")]
)
def update_anc_perf(fy, route, stage_length, flight):
    print(f'Check the value of selected stage_length {stage_length}')
    df_network_data_1 = df_network_data[df_network_data['Distance Category'].isin(stage_length)]
    df_network_grp = df_network_data_1.groupby(['Route', 'Distance Category']).agg({'Take Rate %': 'mean',
                                                                                    'Rev/Pax': 'mean',
                                                                                    'Ancillary RASK': 'mean',
                                                                                    'Total Departures': 'sum',
                                                                                    'Distance': 'max'})
    # df_network_grp['Take Rate %'] = round(df_network_grp['Take Rate %']*100)
    df_network_grp.reset_index(inplace=True)
    df_network_grp.rename(columns={'Distance Category': 'Stage Length(km)'}, inplace=True)
    fig = px.scatter(df_network_grp, x='Rev/Pax', y='Take Rate %',
                     size='Total Departures',
                     color='Route',
                     # facet_row='Stage Length(km)',
                     hover_name='Route',
                     hover_data={'Ancillary RASK': True,
                                 'Rev/Pax': True,
                                 'Take Rate %': True,
                                 'Total Departures': True,
                                 'Distance': True,
                                 'Stage Length(km)': False},
                     #                  custom_data=df_network_grp['Route'],
                     height=700,
                     # width=1000,
                     template='ggplot2',
                     )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(title='Revenue per Pax and Take Rate by Route',
                      title_x=0.5,
                      font=dict(family="Arial", size=15, color="black"),
                      xaxis=dict(tickformat="$"),
                      # yaxis=dict(tickformat=".2%"),
                      plot_bgcolor='rgba(0,0,0,0)',
                      template='ggplot2',
                      legend=dict(
                          # orientation="h",
                          font=dict(size=12),
                          # yanchor="bottom",
                          # y=1.02,
                          # xanchor="right",
                          # x=0.8),
                      ))

    return fig


@app.callback(
    Output("product_perf", "figure"),
    [
        Input("year-financial", "value"),
        Input("market-select", "value"),
        Input("flight-select", "value"),
        Input("anc_kpi_radio_1", "value"),
    ]
)
def update_product_perf(fy, route, flight, anc_kpi):
    df_anc_prod_agg = df_anc_prod_data.groupby('Ancillary Product').agg({'Take Rate': 'sum',
                                                                         'Rev/Pax': 'sum',
                                                                         'RASK': 'sum',
                                                                         'Rev Contr': 'sum'}
                                                                        ).sort_values(by='Rev Contr', ascending=False)

    df_anc_prod_agg['Take Rate'] = round(df_anc_prod_agg['Take Rate'] * 100, 1)
    df_anc_prod_agg['Rev/Pax'] = round(df_anc_prod_agg['Rev/Pax'], 2)
    df_anc_prod_agg['RASK'] = round(df_anc_prod_agg['RASK'], 4)
    df_anc_prod_agg['Rev Contr'] = round(df_anc_prod_agg['Rev Contr'] * 100, 2)
    df_anc_prod_agg['Cum Rev'] = df_anc_prod_agg['Rev Contr'].cumsum()
    df_anc_prod_agg.reset_index(inplace=True)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df_anc_prod_agg['Ancillary Product'],
            y=df_anc_prod_agg['Cum Rev'],
            name="Cumulative Revenue Contribution(%)",
            marker=dict(color="crimson"),
            hovertemplate='Ancillary Product: %{x} <br>Cumulative Revenue: %{y}',
        ), secondary_y=True)

    chosen_kpi = ""
    if anc_kpi == "take_up_rate":
        chosen_kpi = "Take Rate"
        fig.add_trace(
            go.Bar(
                x=df_anc_prod_agg['Ancillary Product'],
                y=df_anc_prod_agg['Take Rate'],
                # name="Take Rate (%)",
                marker=dict(color='#1f77b4'),
                hovertemplate='Ancillary Product: %{x} <br>Take Rate: %{y}',
                opacity=0.7
            ), secondary_y=False, )
        fig.update_yaxes(title_text="Cumulative Revenue Contribution(%)", secondary_y=True)
        fig.update_yaxes(title_text="Take Rate(%)", secondary_y=False)
        fig.update_layout(
            yaxis=dict(
                # type='linear',
                # range=[1, 100],
                ticksuffix='%'),
        )
    elif anc_kpi == "rev_per_pax":
        chosen_kpi = "Revenue per Pax"
        fig.add_trace(
            go.Bar(
                x=df_anc_prod_agg['Ancillary Product'],
                y=df_anc_prod_agg['Rev/Pax'],
                # name="Take Rate (%)",
                marker=dict(color='#1f77b4'),
                hovertemplate='Ancillary Product: %{x} <br>Revenue Per Pax: %{y}',
                opacity=0.7
            ), secondary_y=False, )
        fig.update_yaxes(title_text="Cumulative Revenue Contribution(%)", secondary_y=True)
        fig.update_yaxes(title_text="Revenue Per Pax (USD)", secondary_y=False)
    else:
        chosen_kpi = "RASK"
        fig.add_trace(
            go.Bar(
                x=df_anc_prod_agg['Ancillary Product'],
                y=df_anc_prod_agg['RASK'],
                # name="Take Rate (%)",
                marker=dict(color='#1f77b4'),
                hovertemplate='Ancillary Product: %{x} <br>RASK: %{y}',
                opacity=0.7
            ), secondary_y=False)
        fig.update_yaxes(title_text="Cumulative Revenue Contribution(%)", secondary_y=True)
        fig.update_yaxes(title_text="RASK (USD)", secondary_y=False)

    fig.update_layout(
        title="Ancillary Product " + chosen_kpi + " Performance",
        xaxis_title="Product",
        # yaxis_title="Load Factor Forecast",
        title_x=0.5,
        showlegend=False,
        #     legend=dict(orientation="h"),
        font=dict(family="Arial", size=15, color="black"),
        plot_bgcolor='rgba(0,0,0,0)',
        template='ggplot2',
        height=550,
        # yaxis=dict(
        #     type='linear',
        #     range=[1, 100],
        #     ticksuffix='%'),
        yaxis2=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%')
    )

    return fig


@app.callback(
    Output("sub_product_perf", "figure"),
    [
        Input("year-financial", "value"),
        Input("market-select", "value"),
        Input("flight-select", "value"),
        Input("product_perf", "clickData"),
        Input("anc_kpi_radio_1", "value"),
    ]
)
def update_sub_product_perf(fy, route, flight, prod_input, anc_kpi):
    print(f'Checking the input value of product {prod_input}')

    if prod_input is not None:
        product = prod_input['points'][0]['label']
        print(f'Check the value of product {product}')
        df_anc_prod_data_1 = df_anc_prod_data[(df_anc_prod_data['Ancillary Product'] == product)]
        print(f'Check the value of df_anc_prod_data_1 {df_anc_prod_data_1}')
    else:
        df_anc_prod_data_1 = df_anc_prod_data.copy()

    df_anc_sub_prod_agg = df_anc_prod_data_1.groupby(['Ancillary Product', 'Ancillary Sub-Product']).agg(
        {'Take Rate': 'sum',
         'Rev/Pax': 'sum',
         'RASK': 'sum',
         'Rev Contr': 'sum'}
    ).sort_values(by='Rev Contr', ascending=False)
    df_anc_sub_prod_agg['Take Rate'] = round(df_anc_sub_prod_agg['Take Rate'] * 100, 1)
    df_anc_sub_prod_agg['Rev/Pax'] = round(df_anc_sub_prod_agg['Rev/Pax'], 2)
    df_anc_sub_prod_agg['RASK'] = round(df_anc_sub_prod_agg['RASK'], 4)
    df_anc_sub_prod_agg['Rev Contr'] = round(df_anc_sub_prod_agg['Rev Contr'] * 100, 2)
    df_anc_sub_prod_agg['Cum Rev'] = df_anc_sub_prod_agg['Rev Contr'].cumsum()
    df_anc_sub_prod_agg.reset_index(inplace=True)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df_anc_sub_prod_agg['Ancillary Sub-Product'],
            y=df_anc_sub_prod_agg['Cum Rev'],
            name="Cumulative Revenue Contribution(%)",
            marker=dict(color="crimson"),
            hovertemplate='Ancillary Sub-Product: %{x} <br>Cumulative Revenue: %{y}',
        ), secondary_y=True)

    chosen_kpi = ""
    if anc_kpi == "take_up_rate":
        chosen_kpi = "Take Rate"
        fig.add_trace(
            go.Bar(
                x=df_anc_sub_prod_agg['Ancillary Sub-Product'],
                y=df_anc_sub_prod_agg['Take Rate'],
                # name="Take Rate (%)",
                marker=dict(color='#1f77b4'),
                hovertemplate='Ancillary Sub-Product: %{x} <br>Take Rate: %{y}',
                opacity=0.7
            ), secondary_y=False, )
        fig.update_yaxes(title_text="Cumulative Revenue Contribution(%)", secondary_y=True)
        fig.update_yaxes(title_text="Take Rate(%)", secondary_y=False)
        fig.update_layout(
            yaxis=dict(
                # type='linear',
                # range=[1, 100],
                ticksuffix='%'),
        )
    elif anc_kpi == "rev_per_pax":
        chosen_kpi = "Revenue per Pax"
        fig.add_trace(
            go.Bar(
                x=df_anc_sub_prod_agg['Ancillary Sub-Product'],
                y=df_anc_sub_prod_agg['Rev/Pax'],
                # name="Take Rate (%)",
                marker=dict(color='#1f77b4'),
                hovertemplate='Ancillary Sub-Product: %{x} <br>Revenue Per Pax: %{y}',
                opacity=0.7
            ), secondary_y=False, )
        fig.update_yaxes(title_text="Cumulative Revenue Contribution(%)", secondary_y=True)
        fig.update_yaxes(title_text="Revenue Per Pax (USD)", secondary_y=False)
    else:
        chosen_kpi = "RASK"
        fig.add_trace(
            go.Bar(
                x=df_anc_sub_prod_agg['Ancillary Sub-Product'],
                y=df_anc_sub_prod_agg['RASK'],
                # name="Take Rate (%)",
                marker=dict(color='#1f77b4'),
                hovertemplate='Ancillary Sub-Product: %{x} <br>RASK: %{y}',
                opacity=0.7
            ), secondary_y=False)
        fig.update_yaxes(title_text="Cumulative Revenue Contribution(%)", secondary_y=True)
        fig.update_yaxes(title_text="RASK (USD)", secondary_y=False)

    fig.update_layout(
        title="Ancillary Sub-Product " + chosen_kpi + " Performance",
        xaxis_title="Product",
        xaxis={'tickfont': {'size': 12}},
        # yaxis_title="Load Factor Forecast",
        title_x=0.5,
        showlegend=False,
        font=dict(family="Arial", size=15, color="black"),
        plot_bgcolor='rgba(0,0,0,0)',
        template='ggplot2',
        height=550,
        # yaxis=dict(
        #     type='linear',
        #     range=[1, 100],
        #     ticksuffix='%'),
        yaxis2=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%')
    )

    return fig


@app.callback(
    Output("anc_bkg_prod_trend", "figure"),
    Input("anc_kpi_radio_1", "value"),
)
def generate_dtd_heat_map(anc_kpi):
    chosen_kpi = ""
    if anc_kpi == "take_up_rate":
        chosen_kpi = "Take Rate"
        df_anc_bkg_prod = pd.pivot_table(anc_bkg_prod, values="Take Rate",
                                         index="Ancillary Product",
                                         columns="Booking Product",
                                         aggfunc='sum', fill_value=0,
                                         # sort=False
                                         )
        df_anc_bkg_prod.columns.name = None
        df_anc_bkg_prod.index.name = None
        cols = df_anc_bkg_prod.columns.tolist()
        rows = df_anc_bkg_prod.index.tolist()
        df_anc_bkg_prod = round(df_anc_bkg_prod * 100, 2)
        df_anc_bkg_prod["Cum KPI"] = round(df_anc_bkg_prod.sum(axis=1), 1)
        df_anc_bkg_prod.loc['Total'] = round(df_anc_bkg_prod.sum(axis=0), 1)
        fig = px.imshow(
            df_anc_bkg_prod.iloc[:-1, :-1].values,
            labels=dict(x="Fare Product", y="Ancillary Product", color="Take Rate"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto'
        )
    elif anc_kpi == "rev_per_pax":
        chosen_kpi = "Revenue per Pax"
        df_anc_bkg_prod = pd.pivot_table(anc_bkg_prod, values="Rev/Pax",
                                         index="Ancillary Product",
                                         columns="Booking Product",
                                         aggfunc='mean', fill_value=0,
                                         # sort=False
                                         )
        df_anc_bkg_prod.columns.name = None
        df_anc_bkg_prod.index.name = None
        cols = df_anc_bkg_prod.columns.tolist()
        rows = df_anc_bkg_prod.index.tolist()
        df_anc_bkg_prod = round(df_anc_bkg_prod, 2)
        df_anc_bkg_prod["Cum KPI"] = round(df_anc_bkg_prod.sum(axis=1), 2)
        df_anc_bkg_prod.loc['Total'] = round(df_anc_bkg_prod.sum(axis=0), 2)

        fig = px.imshow(
            df_anc_bkg_prod.iloc[:-1, :-1].values,
            labels=dict(x="Fare Product", y="Ancillary Product", color="Rev/Pax"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto')
    else:
        chosen_kpi = "RASK"
        df_anc_bkg_prod = pd.pivot_table(anc_bkg_prod, values="Ancillary RASK",
                                         index="Ancillary Product",
                                         columns="Booking Product",
                                         aggfunc='mean', fill_value=0,
                                         # sort=False
                                         )
        df_anc_bkg_prod.columns.name = None
        df_anc_bkg_prod.index.name = None
        cols = df_anc_bkg_prod.columns.tolist()
        rows = df_anc_bkg_prod.index.tolist()
        df_anc_bkg_prod = round(df_anc_bkg_prod, 4)
        df_anc_bkg_prod["Cum KPI"] = round(df_anc_bkg_prod.sum(axis=1), 4)
        df_anc_bkg_prod.loc['Total'] = round(df_anc_bkg_prod.sum(axis=0), 4)

        fig = px.imshow(
            df_anc_bkg_prod.iloc[:-1, :-1].values,
            labels=dict(x="Fare Product", y="Ancillary Product", color="Ancillary RASK"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto'
        )

    for i, r in enumerate(df_anc_bkg_prod['Cum KPI']):
        fig.add_shape(type='rect',
                      x0=4.5, y0=-0.5 + i, x1=5.5, y1=0.5 + i,
                      line=dict(
                          color='rgb(188,189,220)',
                          width=1,
                      ),
                      fillcolor='white',
                      )
        fig.add_annotation(
            x=5,
            y=i,
            text=str(r),
            showarrow=False
        )

    for i, c in enumerate(df_anc_bkg_prod.loc['Total'].tolist()):
        if i == 6:
            break
        fig.add_shape(type='rect',
                      x0=-0.5 + i, y0=7.5, x1=0.5 + i, y1=6.5,
                      line=dict(
                          color='rgb(188,189,220)',
                          width=1,
                      ),
                      fillcolor='white',
                      )
        fig.add_annotation(
            x=i,
            y=7.0,
            text=str(c),
            showarrow=False
        )

    fig.add_annotation(
        x=0.95,
        y=-0.09,
        xref='paper',
        yref='paper',
        text='Total',
        showarrow=False,
    )

    fig.add_annotation(
        x=-0.07,
        y=0.03,
        xref='paper',
        yref='paper',
        text='Total',
        showarrow=False,
    )

    fig.update_xaxes(side="bottom")
    fig.update_layout(
        title="Ancillary " + chosen_kpi + " by Fare Product",
        title_x=0.5,
        showlegend=False,
        font=dict(family="Arial", size=15, color="black"),
        coloraxis=dict(showscale=False),
        plot_bgcolor='rgba(0,0,0,0)',
        template='ggplot2'
    )

    return fig


@app.callback(
    Output("anc_bkg_channel_trend", "figure"),
    Input("anc_kpi_radio_1", "value"),
)
def generate_dtd_heat_map(anc_kpi):
    chosen_kpi = ""
    if anc_kpi == "take_up_rate":
        chosen_kpi = "Take Rate"
        df_anc_bkg_prod = pd.pivot_table(anc_dist_chan, values="Take Rate",
                                         index="Ancillary Product",
                                         columns="Channel",
                                         aggfunc='mean', fill_value=0,
                                         # sort=False
                                         )
        df_anc_bkg_prod.columns.name = None
        df_anc_bkg_prod.index.name = None
        cols = df_anc_bkg_prod.columns.tolist()
        rows = df_anc_bkg_prod.index.tolist()
        df_anc_bkg_prod = round(df_anc_bkg_prod * 100, 2)
        df_anc_bkg_prod["Cum KPI"] = round(df_anc_bkg_prod.sum(axis=1), 1)
        df_anc_bkg_prod.loc['Total'] = round(df_anc_bkg_prod.sum(axis=0), 1)

        fig = px.imshow(
            df_anc_bkg_prod.iloc[:-1, :-1].values,
            labels=dict(x="Channel", y="Ancillary Product", color="Take Rate"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto'
        )
    elif anc_kpi == "rev_per_pax":
        chosen_kpi = "Revenue per Pax"
        df_anc_bkg_prod = pd.pivot_table(anc_dist_chan, values="Rev/Pax",
                                         index="Ancillary Product",
                                         columns="Channel",
                                         aggfunc='mean', fill_value=0,
                                         # sort=False
                                         )
        df_anc_bkg_prod.columns.name = None
        df_anc_bkg_prod.index.name = None
        cols = df_anc_bkg_prod.columns.tolist()
        rows = df_anc_bkg_prod.index.tolist()
        df_anc_bkg_prod = round(df_anc_bkg_prod, 2)
        df_anc_bkg_prod["Cum KPI"] = round(df_anc_bkg_prod.sum(axis=1), 2)
        df_anc_bkg_prod.loc['Total'] = round(df_anc_bkg_prod.sum(axis=0), 2)

        fig = px.imshow(
            df_anc_bkg_prod.iloc[:-1, :-1].values,
            labels=dict(x="Channel", y="Ancillary Product", color="Rev/Pax"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto')
    else:
        chosen_kpi = "RASK"
        df_anc_bkg_prod = pd.pivot_table(anc_dist_chan, values="Ancillary RASK",
                                         index="Ancillary Product",
                                         columns="Channel",
                                         aggfunc='mean', fill_value=0,
                                         # sort=False
                                         )
        df_anc_bkg_prod.columns.name = None
        df_anc_bkg_prod.index.name = None
        cols = df_anc_bkg_prod.columns.tolist()
        rows = df_anc_bkg_prod.index.tolist()
        df_anc_bkg_prod["Cum KPI"] = df_anc_bkg_prod.sum(axis=1)
        df_anc_bkg_prod.loc['Total'] = df_anc_bkg_prod.sum(axis=0)
        df_anc_bkg_prod = round(df_anc_bkg_prod, 4)
        fig = px.imshow(
            df_anc_bkg_prod.iloc[:-1, :-1].values,
            labels=dict(x="Channel", y="Ancillary Product", color="Ancillary RASK"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto'
        )

    for i, r in enumerate(df_anc_bkg_prod['Cum KPI']):
        fig.add_shape(type='rect',
                      x0=4.5, y0=-0.5 + i, x1=5.5, y1=0.5 + i,
                      line=dict(
                          color='rgb(188,189,220)',
                          width=1,
                      ),
                      fillcolor='white',
                      )
        fig.add_annotation(
            x=5,
            y=i,
            text=str(r),
            showarrow=False
        )

    for i, c in enumerate(df_anc_bkg_prod.loc['Total'].tolist()):
        if i == 6:
            break
        fig.add_shape(type='rect',
                      x0=-0.5 + i, y0=7.5, x1=0.5 + i, y1=6.5,
                      line=dict(
                          color='rgb(188,189,220)',
                          width=1,
                      ),
                      fillcolor='white',
                      )
        fig.add_annotation(
            x=i,
            y=7.0,
            text=str(c),
            showarrow=False
        )

    fig.add_annotation(
        x=0.95,
        y=-0.09,
        xref='paper',
        yref='paper',
        text='Total',
        showarrow=False,
    )

    fig.add_annotation(
        x=-0.07,
        y=0.03,
        xref='paper',
        yref='paper',
        text='Total',
        showarrow=False,
    )

    fig.update_xaxes(side="bottom")
    fig.update_layout(
        title="Ancillary " + chosen_kpi + " by Purchased Channel",
        # xaxis_title="Product",
        title_x=0.5,
        showlegend=False,
        # legend=dict(orientation="h"),
        font=dict(family="Arial", size=15, color="black"),
        coloraxis=dict(showscale=False),
        plot_bgcolor='rgba(0,0,0,0)',
        template='ggplot2'
    )

    return fig


@app.callback(
    Output("anc_seat_map", "figure"),
    # Input("year-financial", "value"),
    [Input("anc_kpi_radio_1", "value"),
     Input("product_perf", "clickData")],
)
def generate_dtd_heat_map(anc_kpi, prod_input):
    if prod_input is not None:
        product = prod_input['points'][0]['label']
        print(f'Check the value of product in booking dtd range {product}')
        df_anc_dtd_data_1 = df_anc_dtd_data[df_anc_dtd_data['Ancillary Product'] == product]
        # df_anc_prod_data_1 = df_anc_prod_data[(df_anc_prod_data['Ancillary Product'] == product)]
        # print(f'Check the value of df_anc_prod_data_1 {df_anc_prod_data_1}')
    else:
        df_anc_dtd_data_1 = df_anc_dtd_data.copy()

    chosen_kpi = ""
    if anc_kpi == "take_up_rate":
        chosen_kpi = "Take Rate"
        anc_dtd_bkg = pd.pivot_table(df_anc_dtd_data_1,
                                     values="Take Rate",
                                     index="Ancillary Purchase DTD Range",
                                     columns="Booking DTD Range",
                                     aggfunc="sum",
                                     fill_value=0)
        anc_dtd_bkg.columns.name = None
        anc_dtd_bkg.index.name = None
        cols = anc_dtd_bkg.columns.tolist()
        rows = anc_dtd_bkg.index.tolist()
        anc_dtd_bkg = round(anc_dtd_bkg * 100, 2)
        anc_dtd_bkg["Cum KPI"] = round(anc_dtd_bkg.sum(axis=1), 1)
        anc_dtd_bkg.loc['Total'] = round(anc_dtd_bkg.sum(axis=0), 1)

        fig = px.imshow(
            anc_dtd_bkg.iloc[:-1, :-1].values,
            labels=dict(x="Booking DTD Range", y="Ancillary Purchase DTD Range", color="Take Rate"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto',
        )

    elif anc_kpi == "rev_per_pax":
        chosen_kpi = "Revenue per Pax"
        anc_dtd_bkg = pd.pivot_table(df_anc_dtd_data,
                                     values="Rev/Pax",
                                     index="Ancillary Purchase DTD Range",
                                     columns="Booking DTD Range",
                                     aggfunc="sum",
                                     fill_value=0)
        anc_dtd_bkg.columns.name = None
        anc_dtd_bkg.index.name = None
        cols = anc_dtd_bkg.columns.tolist()
        rows = anc_dtd_bkg.index.tolist()
        anc_dtd_bkg = round(anc_dtd_bkg, 2)
        anc_dtd_bkg["Cum KPI"] = round(anc_dtd_bkg.sum(axis=1), 1)
        anc_dtd_bkg.loc['Total'] = round(anc_dtd_bkg.sum(axis=0), 1)
        fig = px.imshow(
            anc_dtd_bkg.iloc[:-1, :-1].values,
            labels=dict(x="Booking DTD Range", y="Ancillary Purchase DTD Range", color="Rev/Pax"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto'
        )
    else:
        chosen_kpi = "RASK"
        anc_dtd_bkg = pd.pivot_table(df_anc_dtd_data,
                                     values="RASK",
                                     index="Ancillary Purchase DTD Range",
                                     columns="Booking DTD Range",
                                     aggfunc="sum",
                                     fill_value=0)
        anc_dtd_bkg.columns.name = None
        anc_dtd_bkg.index.name = None
        cols = anc_dtd_bkg.columns.tolist()
        rows = anc_dtd_bkg.index.tolist()
        anc_dtd_bkg = round(anc_dtd_bkg, 4)
        anc_dtd_bkg["Cum KPI"] = round(anc_dtd_bkg.sum(axis=1), 4)
        anc_dtd_bkg.loc['Total'] = round(anc_dtd_bkg.sum(axis=0), 4)

        fig = px.imshow(
            anc_dtd_bkg.iloc[:-1, :-1].values,
            labels=dict(x="Booking DTD Range", y="Ancillary Purchase DTD Range", color="RASK"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto'
        )

    for i, r in enumerate(anc_dtd_bkg['Cum KPI']):
        fig.add_shape(type='rect',
                      x0=6.5, y0=-0.5 + i, x1=7.5, y1=0.5 + i,
                      line=dict(
                          color='rgb(188,189,220)',
                          width=1,
                      ),
                      fillcolor='white',
                      )
        fig.add_annotation(
            x=7,
            y=i,
            text=str(r),
            showarrow=False
        )

    for i, c in enumerate(anc_dtd_bkg.loc['Total'].tolist()):
        if i == 7:
            break
        fig.add_shape(type='rect',
                      x0=-0.5 + i, y0=7.5, x1=0.5 + i, y1=6.5,
                      line=dict(
                          color='rgb(188,189,220)',
                          width=1,
                      ),
                      fillcolor='white',
                      )
        fig.add_annotation(
            x=i,
            y=7.0,
            text=str(c),
            showarrow=False
        )

    fig.add_annotation(
        x=0.96,
        y=-0.09,
        xref='paper',
        yref='paper',
        text='Total',
        showarrow=False,
    )

    fig.add_annotation(
        x=-0.05,
        y=0.05,
        xref='paper',
        yref='paper',
        text='Total',
        showarrow=False,
    )

    fig.update_xaxes(side="bottom")
    fig.update_layout(
        title="Ancillary " + chosen_kpi + " by Booked and Ancillary Purchase DTD Range ",
        # xaxis_title="Product",
        title_x=0.5,
        yaxis={'autorange': 'reversed'},
        showlegend=False,
        # legend=dict(orientation="h"),
        font=dict(family="Arial", size=15, color="black"),
        coloraxis=dict(showscale=False),
        plot_bgcolor='rgba(0,0,0,0)',
        template='ggplot2'
    )

    return fig


@app.callback(
    Output("anc_seat_map_1", "figure"),
    Input("anc_kpi_radio_1", "value"),
)
def generate_channel_heat_map(anc_kpi):
    chosen_kpi = ""
    if anc_kpi == "take_up_rate":
        chosen_kpi = "Take Rate"
        df_anc_bkg_prod = pd.pivot_table(anc_dist_chan, values="Take Rate",
                                         index="Channel",
                                         columns="Booking Channel",
                                         aggfunc='mean', fill_value=0,
                                         # sort=False
                                         )
        df_anc_bkg_prod.columns.name = None
        df_anc_bkg_prod.index.name = None
        cols = df_anc_bkg_prod.columns.tolist()
        rows = df_anc_bkg_prod.index.tolist()
        df_anc_bkg_prod = round(df_anc_bkg_prod * 100, 2)
        df_anc_bkg_prod["Cum KPI"] = round(df_anc_bkg_prod.sum(axis=1), 1)
        df_anc_bkg_prod.loc['Total'] = round(df_anc_bkg_prod.sum(axis=0), 1)

        fig = px.imshow(
            df_anc_bkg_prod.iloc[:-1, :-1].values,
            labels=dict(x="Product Booking Channel", y="Ancillary Purchased Channel", color="Take Rate"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto'
        )
    elif anc_kpi == "rev_per_pax":
        chosen_kpi = "Revenue per Pax"
        df_anc_bkg_prod = pd.pivot_table(anc_dist_chan, values="Rev/Pax",
                                         index="Channel",
                                         columns="Booking Channel",
                                         aggfunc='mean', fill_value=0,
                                         # sort=False
                                         )
        df_anc_bkg_prod.columns.name = None
        df_anc_bkg_prod.index.name = None
        cols = df_anc_bkg_prod.columns.tolist()
        rows = df_anc_bkg_prod.index.tolist()
        df_anc_bkg_prod = round(df_anc_bkg_prod, 2)
        df_anc_bkg_prod["Cum KPI"] = round(df_anc_bkg_prod.sum(axis=1), 2)
        df_anc_bkg_prod.loc['Total'] = round(df_anc_bkg_prod.sum(axis=0), 2)

        fig = px.imshow(
            df_anc_bkg_prod.iloc[:-1, :-1].values,
            labels=dict(x="Product Booking Channel", y="Ancillary Purchased Channel", color="Rev/Pax"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto')
    else:
        chosen_kpi = "RASK"
        df_anc_bkg_prod = pd.pivot_table(anc_dist_chan, values="Ancillary RASK",
                                         index="Channel",
                                         columns="Booking Channel",
                                         aggfunc='mean', fill_value=0
                                         )
        df_anc_bkg_prod.columns.name = None
        df_anc_bkg_prod.index.name = None
        cols = df_anc_bkg_prod.columns.tolist()
        rows = df_anc_bkg_prod.index.tolist()
        df_anc_bkg_prod["Cum KPI"] = df_anc_bkg_prod.sum(axis=1)
        df_anc_bkg_prod.loc['Total'] = df_anc_bkg_prod.sum(axis=0)
        df_anc_bkg_prod = round(df_anc_bkg_prod, 4)
        fig = px.imshow(
            df_anc_bkg_prod.iloc[:-1, :-1].values,
            labels=dict(x="Product Booking Channel", y="Ancillary Purchased Channel", color="Ancillary RASK"),
            x=cols,
            y=rows,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto='auto'
        )

    for i, r in enumerate(df_anc_bkg_prod['Cum KPI']):
        fig.add_shape(type='rect',
                      x0=3.5, y0=-0.5 + i, x1=4.5, y1=0.5 + i,
                      line=dict(
                          color='rgb(188,189,220)',
                          width=1,
                      ),
                      fillcolor='white',
                      )
        fig.add_annotation(
            x=4,
            y=i,
            text=str(r),
            showarrow=False
        )

    for i, c in enumerate(df_anc_bkg_prod.loc['Total'].tolist()):
        if i == 5:
            break
        fig.add_shape(type='rect',
                      x0=-0.5 + i, y0=5.5, x1=0.5 + i, y1=4.5,
                      line=dict(
                          color='rgb(188,189,220)',
                          width=1,
                      ),
                      fillcolor='white',
                      )
        fig.add_annotation(
            x=i,
            y=5.0,
            text=str(c),
            showarrow=False
        )

    fig.add_annotation(
        x=0.92,
        y=-0.09,
        xref='paper',
        yref='paper',
        text='Total',
        showarrow=False,
    )

    fig.add_annotation(
        x=-0.07,
        y=0.03,
        xref='paper',
        yref='paper',
        text='Total',
        showarrow=False,
    )

    fig.update_xaxes(side="bottom")
    fig.update_layout(
        title="Ancillary " + chosen_kpi + " by Ancillary Purchase Channel vs Booked Channel",
        # xaxis_title="Product",
        title_x=0.5,
        showlegend=False,
        # legend=dict(orientation="h"),
        font=dict(family="Arial", size=15, color="black"),
        plot_bgcolor='rgba(0,0,0,0)',
        template='ggplot2',
        coloraxis=dict(showscale=False)
    )

    return fig


@app.callback(
    Output("anc_seat_map_2", "figure"),
    [Input("anc_kpi_radio", "value"),
     Input("product-checkbox", "value")]
)
def generate_seat_heat_map(anc_kpi, product_list):
    if anc_kpi == "take_up_rate":
        df_tr_1 = df_tr[df_tr['Product'].isin(product_list)]
        df_seat_pivot = pd.pivot_table(df_tr_1, values="Take Rate", index="Column", columns="Rows",
                                       aggfunc='mean', fill_value=0)
        df_seat_pivot = df_seat_pivot * 100
        df_seat_pivot = round(df_seat_pivot)
        heatmap_data_seat = df_seat_pivot.values.tolist()
        x_labels = df_seat_pivot.columns.tolist()
        x_vals = [str(x) for x in x_labels]
        y_labels = df_seat_pivot.index.tolist()
        fig = px.imshow(heatmap_data_seat,
                        labels=dict(x="Rows", y="Column", color="Take-up Rate %"),
                        x=x_vals,
                        y=y_labels,
                        text_auto=True,
                        aspect="auto",
                        color_continuous_scale='Blues',
                        origin='lower')
        fig.update_xaxes(side="bottom")
        fig.update_layout(
            title="Take Rate performance by Seat Map ",
            title_x=0.5,
            showlegend=False,
            # legend=dict(orientation="h"),
            font=dict(family="Arial", size=15, color="black"),
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis=dict(showscale=False),
            template='ggplot2')
    elif anc_kpi == "rev_per_pax":
        df_rpp_1 = df_rpp[df_rpp['Product'].isin(product_list)]
        df_seat_pivot_1 = pd.pivot_table(df_rpp_1, values="Rev/Pax", index="Column", columns="Rows",
                                         aggfunc='mean', fill_value=0)
        df_seat_pivot_1 = round(df_seat_pivot_1, 1)
        heatmap_data_seat_1 = df_seat_pivot_1.values.tolist()
        x_labels = df_seat_pivot_1.columns.tolist()
        x_vals = [str(x) for x in x_labels]
        y_labels = df_seat_pivot_1.index.tolist()
        fig = px.imshow(heatmap_data_seat_1,
                        labels=dict(x="Rows", y="Column", color="Revenue Per Pax (USD)"),
                        x=x_vals,
                        y=y_labels,
                        text_auto=True, aspect="auto",
                        # color_continuous_scale='RdBu_r',
                        color_continuous_scale='Blues',
                        origin='lower')
        fig.update_xaxes(side="bottom")
        fig.update_layout(
            title="Revenue Per Pax by Seat Map ",
            title_x=0.5,
            showlegend=False,
            # legend=dict(orientation="h"),
            font=dict(family="Arial", size=15, color="black"),
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis=dict(showscale=False),
            template='ggplot2')
    else:
        df_rask_1 = df_rask[df_rask['Product'].isin(product_list)]
        df_seat_pivot_2 = pd.pivot_table(df_rask_1, values="RASK", index="Column", columns="Rows",
                                         aggfunc='mean', fill_value=0)
        df_seat_pivot_2 = round(df_seat_pivot_2, 3)
        heatmap_data_seat_2 = df_seat_pivot_2.values.tolist()
        x_labels = df_seat_pivot_2.columns.tolist()
        x_vals = [str(x) for x in x_labels]
        y_labels = df_seat_pivot_2.index.tolist()
        fig = px.imshow(heatmap_data_seat_2,
                        labels=dict(x="Rows", y="Column", color="Ancillary RASK (USD)"),
                        x=x_vals,
                        y=y_labels,
                        text_auto=True, aspect="auto",
                        # color_continuous_scale='RdBu_r',
                        color_continuous_scale='Blues',
                        origin='lower')
        fig.update_xaxes(side="bottom")
        fig.update_layout(
            title="Ancillary RASK by Seat Map ",
            title_x=0.5,
            # xaxis=dict(
            #     type='linear',
            #     range=[1, 30],
            #     ),
            showlegend=False,
            # legend=dict(orientation="h"),
            font=dict(family="Arial", size=15, color="black"),
            plot_bgcolor='rgba(0,0,0,0)',
            coloraxis=dict(showscale=False),
            template='ggplot2')

    return fig


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
