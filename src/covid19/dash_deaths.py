import covid19.dash_app
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from .dash_app import app
from .data import DAY_ZERO_START

tab_deaths = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Select one or more countries"),
                            dcc.Dropdown(
                                id="deaths-countries-selector",
                                value=covid19.dash_app.DROPDOWN_SELECTED_COUNTRIES,
                                # options=covid19.dash_app.all_countries,
                                multi=True,
                                clearable=False,
                            ),
                        ]
                    ),
                    md=6,
                ),
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Select plot scale"),
                            dbc.RadioItems(
                                id="deaths-plot-scale",
                                options=[
                                    {"value": "linear", "label": "Linear"},
                                    {"value": "log", "label": "Logarithmic"},
                                ],
                                value="linear",
                            ),
                        ]
                    ),
                    md=6,
                ),
            ]
        ),
        dbc.Row([dbc.Col(dcc.Graph(id="deaths-per-pop-figure"), md=12)]),
        dbc.Row([dbc.Col(dcc.Graph(id="deaths-per-inf-figure"), md=12)]),
    ]
)


# Update the options of the country-selector
@app.callback(
    Output("deaths-countries-selector", "options"),
    [Input("interval-component", "n_intervals")],
)
def deaths_countries_selector_options(*_):
    return covid19.dash_app.all_countries


@app.callback(
    Output("deaths-per-pop-figure", "figure"),
    [Input("deaths-countries-selector", "value"), Input("deaths-plot-scale", "value")],
)
def deaths_per_pop_figure_figure(countries_to_plot, y_axis_type):
    deaths = covid19.dash_app.deaths
    population = covid19.dash_app.population

    fig = go.Figure(
        layout={
            "title": "Deaths per population size",
            "xaxis": {
                "title": (
                    f"Days since more that {DAY_ZERO_START}"
                    f" people confirmed infected"
                )
            },
            "yaxis": {"title": f"Deaths per 100.000 population", "type": y_axis_type},
        }
    )
    for country in countries_to_plot:
        data = (
            deaths[country].dropna() / population.loc[country, "Population"] * 100_000
        )
        fig.add_trace(
            go.Scatter(x=data.index, y=data.values, name=country, mode="lines")
        )
    return fig


@app.callback(
    Output("deaths-per-inf-figure", "figure"),
    [Input("deaths-countries-selector", "value")],
)
def deaths_per_inf_figure_figure(countries_to_plot):
    infected = covid19.dash_app.infected
    deaths = covid19.dash_app.deaths
    fig = go.Figure(
        layout={
            "title": "Deaths per confirmed infected (CFR)",
            "xaxis": {
                "title": f"Days since more that {DAY_ZERO_START}"
                " people confirmed infected"
            },
            "yaxis": {"title": f"Deaths per infected (CFR)"},
        }
    )
    for country in countries_to_plot:
        data = (deaths[country] / infected[country]).dropna()
        fig.add_trace(
            go.Scatter(x=data.index, y=data.values, name=country, mode="lines")
        )
    return fig
