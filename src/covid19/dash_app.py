import covid19.data
import covid19.forecast
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from covid19.data import DAY_ZERO_START
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN],
                meta_tags=[
                    {'name': 'viewport',
                     'content': 'width=device-width, initial-scale=1'}
                ],
                suppress_callback_exceptions=True)
app.title = "Corona Dashboard"


# Load data once
infected, deaths, population = covid19.data.get_shifted_data()
inf_per_pop = infected / population.loc[infected.columns, "Population"] * 100_000
dea_per_pop = deaths / population.loc[infected.columns, "Population"] * 100_000


footer = html.Div([
    html.H3("Data source"),
    dcc.Markdown("""
        COVID-data is downloaded from 
        [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19)
    """),
    html.H3("About the author"),
    dcc.Markdown("""
        Plots and model created by [Martin Høy](mailto:martin@hoy.priv.no), 
        March 2020.    
    """)
])

# The layout is divided in tabs
app.layout = dbc.Container(
    dbc.Row(dbc.Col(
        [
            html.H1("COVID-19: Current status and possible future",
                    className="mt-4 mb-4"),
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="Current situation",
                        tab_id="tab-current",
                        labelClassName="h3 mb-0",
                    ),
                    dbc.Tab(
                        label="Forecast",
                        tab_id="tab-forecast",
                        labelClassName="h3 mb-0",
                    ),
                ],
                id="tabs",
                active_tab="tab-current",
                className="mb-4"
            ),
            html.Div(id="tabs-content"),

            footer
        ]
    ))
)


tab_current = html.Div([
    dbc.Row([
        dbc.Col([
            html.Label("Select one or more countries"),
            dcc.Dropdown(
                id="multiple-countries-selector",
                options=[{"label": country, "value": country} for country in
                         infected.columns],
                value=[
                    "Norway", "Sweden", "Denmark", "Italy", "Spain", "China"
                ],
                multi=True,
                clearable=False)
        ], md=6, style={"margin-bottom": "1.5rem"}),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='current-figure'), md=12)
    ]),
])


tab_forecast = html.Div([
    dbc.Row([
        dbc.Col([
            html.Label("Select country"),
            dcc.Dropdown(
                id="country-selector",
                options=[{"label": country, "value": country} for country in
                         infected.columns],
                value="Norway",
                clearable=False,
                className="mb-4")
        ], md=6),
        dbc.Col([
            html.Label("The day when spreading is under control"),
            dcc.Slider(
                id="day-of-control",
                min=30, max=120, step=10,
                marks={i: f"{i}" for i in range(30, 121, 10)},
                value=60),
        ], md=6),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Factor of unrecorded cases"),
            dcc.Slider(
                id="unrecorded-factor",
                min=1, max=5, step=1,
                marks={i: f"{i}" for i in range(1, 6)},
                value=2),
        ], md=6),
        dbc.Col([
            html.Label("Number of days it takes to recover from the infection"),
            dcc.Slider(
                id="recovery-days",
                min=5, max=25, step=5,
                marks={i: f"{i}" for i in range(5, 26, 5)},
                value=15)
        ], md=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='forecast-figure'), md=12)
    ]),

    dbc.Row([
       dbc.Col([
            html.H3("About the model"),
            dcc.Markdown("""
            This is how the forecast model works:
            
            The measures taken in e.g. China and South Korea have shown that they were
            able to drive the growth towards 1.0 in an exponential way. 
            **NB: The model assumes that the country in question is taking measures
            that are as effective as the ones taken in China**
            
            * The current growth rate is estimated by using an exponentially weighted
                average of the last 7 days.
            * The growth rate is assumed to converge towards 1.0 in an exponential
                decay.
                The speed of the decay is controlled by the parameter "Day when under 
                control" below.
            * Patients are assumed to be ill from the day they are infected.
            * They are assumed to have recovered after the number of days you specify.
            """),
            ])
    ])

])


# This function activates the selected tab
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'active_tab')])
def render_content(tab):
    if tab == 'tab-current':
        return tab_current
    elif tab == 'tab-forecast':
        return tab_forecast


@app.callback(
    dash.dependencies.Output("current-figure", "figure"),
    [dash.dependencies.Input("multiple-countries-selector", "value")])
def create_current_plot(countries):
    """Creates a plot with the current situation"""

    fig = go.Figure(
        layout={
            "title": "Confirmed infected per population size",
            "xaxis": {
                "title":
                    f"Days since more that {DAY_ZERO_START} people confirmed infected"
            },
            "yaxis": {
                "title":
                    f"Confirmed infected per 100.000 population"
            },
        }
    )
    for country in countries:
        fig.add_trace(go.Scatter(
            x=inf_per_pop.index,
            y=inf_per_pop[country].values,
            name=country,
            mode="lines"
        ))

    return fig


@app.callback(
    dash.dependencies.Output("forecast-figure", "figure"),
    [dash.dependencies.Input("country-selector", "value"),
     dash.dependencies.Input("day-of-control", "value"),
     dash.dependencies.Input("unrecorded-factor", "value"),
     dash.dependencies.Input("recovery-days", "value")])
def create_forecast_plot(country, day_of_control=30, unrecorded_factor=1,
                         recovery_days=14):
    """This creates the figure with the forecasts
    """
    observed_data, forecast, being_ill = covid19.forecast.create_forecast(
        infected[country],
        day_of_control=day_of_control,
        days_to_recover=recovery_days,
        forecast_start=-1,
        ratio_avg_days=4)

    observed_data *= unrecorded_factor
    forecast *= unrecorded_factor
    being_ill *= unrecorded_factor

    fig = go.Figure(
            layout={
                "title": "Forecast: Number of infected",
                "xaxis": {
                    "title":
                    f"Days since more that {DAY_ZERO_START} people confirmed infected"}
            }
    )
    fig.add_trace(go.Scatter(
        x=observed_data.index,
        y=observed_data.values,
        name="Currently infected",
        line=dict(color="green", width=8),
        mode="lines"
    ))
    fig.add_trace(go.Scatter(
        x=forecast.index,
        y=forecast.values,
        name="Forecast infected",
        line=dict(color="green", width=3, dash="dash"),
        mode="lines"
    ))
    fig.add_trace(go.Scatter(
        x=being_ill.index,
        y=being_ill.values,
        name="People being ill",
        line=dict(color="orange", width=3, dash="dash"),
        mode="lines"
    ))
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
