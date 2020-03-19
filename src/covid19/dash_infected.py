import covid19.data
import covid19.forecast
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from .dash_app import app, DROPDOWN_SELECTED_COUNTRIES, DROPDOWN_COUNTRIES_OPTIONS
from .data import DAY_ZERO_START

infected, deaths, population = covid19.data.get_shifted_data()
inf_per_pop = infected / population.loc[infected.columns, "Population"] * 100_000

tab_infected = html.Div([
    dbc.Row([
        dbc.Col([
            html.Label("Select one or more countries"),
            dcc.Dropdown(
                id="infected-countries-selector",
                options=DROPDOWN_COUNTRIES_OPTIONS,
                value=DROPDOWN_SELECTED_COUNTRIES,
                multi=True,
                clearable=False)
        ], md=6, style={"margin-bottom": "1.5rem"}),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='infected-figure'), md=12)
    ]),
])


@app.callback(
    dash.dependencies.Output("infected-figure", "figure"),
    [dash.dependencies.Input("infected-countries-selector", "value")])
def create_current_plot(countries_to_plot):
    """Creates a plot with the number of infected"""
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
    for country in countries_to_plot:
        data = inf_per_pop[country].dropna()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data.values,
            name=country,
            mode="lines"
        ))
    return fig
