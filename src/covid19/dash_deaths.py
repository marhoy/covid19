import covid19.data
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from .dash_app import app, DROPDOWN_SELECTED_COUNTRIES, DROPDOWN_COUNTRIES_OPTIONS
from .data import DAY_ZERO_START

infected, deaths, population = covid19.data.get_shifted_data()


tab_deaths = html.Div([
    dbc.Row([
        dbc.Col([
            html.Label("Select one or more countries"),
            dcc.Dropdown(
                id="deaths-countries-selector",
                options=DROPDOWN_COUNTRIES_OPTIONS,
                value=DROPDOWN_SELECTED_COUNTRIES,
                multi=True,
                clearable=False)
        ], md=6, style={"margin-bottom": "1.5rem"}),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='deaths-per-pop-figure'), md=12)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='deaths-per-inf-figure'), md=12)
    ]),
])


@app.callback(
    dash.dependencies.Output("deaths-per-pop-figure", "figure"),
    [dash.dependencies.Input("deaths-countries-selector", "value")])
def create_current_plot(countries_to_plot):
    """Creates a plot with the number of infected"""
    fig = go.Figure(
        layout={
            "title": "Deaths per population size",
            "xaxis": {
                "title":
                    f"Days since more that {DAY_ZERO_START} people confirmed infected"
            },
            "yaxis": {
                "title":
                    f"Deaths per 100.000 population"
            },
        }
    )
    for country in countries_to_plot:
        data = deaths[country].dropna() / population.loc[country, "Population"] * \
               100_000
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data.values,
            name=country,
            mode="lines"
        ))
    return fig


@app.callback(
    dash.dependencies.Output("deaths-per-inf-figure", "figure"),
    [dash.dependencies.Input("deaths-countries-selector", "value")])
def create_current_plot(countries_to_plot):
    """Creates a plot with the number of infected"""
    fig = go.Figure(
        layout={
            "title": "Deaths per confirmed infected",
            "xaxis": {
                "title":
                    f"Days since more that {DAY_ZERO_START} people confirmed infected"
            },
            "yaxis": {
                "title":
                    f"Deaths per infected"
            },
        }
    )
    for country in countries_to_plot:
        data = (deaths[country]/ infected[country]).dropna()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data.values,
            name=country,
            mode="lines"
        ))
    return fig
