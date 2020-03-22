import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

import covid19.forecast
from covid19.data import DAY_ZERO_START

from .dash_app import app

tab_forecast = html.Div([

    dbc.Row([
        dbc.Col(dbc.FormGroup([
            dbc.Label("Select country"),
            dcc.Dropdown(
                id="forecast-country-selector",
                value="Norway",
                clearable=False)
        ]), md=6),

        dbc.Col(dbc.FormGroup([
            dbc.Label("The day when spreading is under control"),
            dcc.Slider(
                id="day-of-control",
                min=30, max=120, step=10,
                marks={i: f"{i}" for i in range(30, 121, 10)},
                value=60),
        ]), md=6),
    ]),

    dbc.Row([
        dbc.Col(dbc.FormGroup([
            dbc.Label("Factor of unrecorded cases"),
            dcc.Slider(
                id="unrecorded-factor",
                min=1, max=5, step=1,
                marks={i: f"{i}" for i in range(1, 6)},
                value=2),
        ]), md=6),

        dbc.Col(dbc.FormGroup([
            dbc.Label("Number of days it takes to recover from the infection"),
            dcc.Slider(
                id="recovery-days",
                min=5, max=25, step=5,
                marks={i: f"{i}" for i in range(5, 26, 5)},
                value=15)
        ]), md=6)
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


@app.callback(Output("forecast-country-selector", "options"),
              [Input("forecast-country-selector", "value")])
def get_all_countries(*_):
    return covid19.dash_app.all_countries


@app.callback(
    Output("forecast-figure", "figure"),
    [Input("forecast-country-selector", "value"),
     Input("day-of-control", "value"),
     Input("unrecorded-factor", "value"),
     Input("recovery-days", "value")])
def create_forecast_plot(country, day_of_control=30, unrecorded_factor=1,
                         recovery_days=14):
    """This creates the figure with the forecasts
    """
    infected = covid19.dash_app.infected

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
                    f"Days since more that {DAY_ZERO_START} people confirmed infected"},
                "yaxis": {
                },
                "margin": dict(t=40, l=20, r=20)
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
