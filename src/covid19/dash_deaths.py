"""Create the tab with deaths."""
from typing import List

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

import covid19.dash_app

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
                            dbc.Label("Plot options"),
                            dbc.Checklist(
                                options=[
                                    {
                                        "label": "Logarithmic scale",
                                        "value": "log_scale",
                                    },
                                    {
                                        "label": "Per population size",
                                        "value": "per_pop_size",
                                    },
                                ],
                                value=["per_pop_size"],
                                id="deaths-plot-options",
                                switch=True,
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
def deaths_countries_selector_options(*_) -> List[dict]:
    """Scheduled update of the possible countries."""
    return covid19.dash_app.all_countries


@app.callback(
    Output("deaths-per-pop-figure", "figure"),
    [
        Input("deaths-countries-selector", "value"),
        Input("deaths-plot-options", "value"),
    ],
)
def deaths_per_pop_figure_figure(
    countries_to_plot: List[str], plot_options: List[str]
) -> go.Figure:
    """Create the death-per-pop figure."""
    # Handle plot options
    if "log_scale" in plot_options:
        y_axis_type = "log"
    else:
        y_axis_type = "linear"
    if "per_pop_size" in plot_options:
        fig_title = "Deaths per 100.000 population"
        y_axis_title = "Deaths per 100.000"
        hoverformat = ".1f"
    else:
        fig_title = "Death numbers in total"
        y_axis_title = "Deaths total"
        hoverformat = ".0f"

    deaths = covid19.dash_app.deaths
    population = covid19.dash_app.population

    fig = go.Figure(
        layout={
            "title": fig_title,
            "xaxis": {
                "title": (
                    f"Days since more that {DAY_ZERO_START}"
                    f" people confirmed infected"
                )
            },
            "yaxis": {
                "title": y_axis_title,
                "type": y_axis_type,
                "hoverformat": hoverformat,
            },
            "margin": {"l": 0, "r": 0},
        }
    )
    for country in countries_to_plot:
        if "per_pop_size" in plot_options:
            data = (
                deaths[country].dropna()
                / population.loc[country, "Population"]
                * 100_000
            )
        else:
            data = deaths[country].dropna()
        fig.add_trace(
            go.Scatter(x=data.index, y=data.values, name=country, mode="lines")
        )
    return fig


@app.callback(
    Output("deaths-per-inf-figure", "figure"),
    [Input("deaths-countries-selector", "value")],
)
def deaths_per_inf_figure_figure(countries_to_plot: List[str]) -> go.Figure:
    """Create the figure with Case Fatality Rate."""
    infected = covid19.dash_app.infected
    deaths = covid19.dash_app.deaths
    fig = go.Figure(
        layout={
            "title": "Deaths per confirmed infected (CFR)",
            "xaxis": {
                "title": f"Days since more that {DAY_ZERO_START}"
                " people confirmed infected"
            },
            "yaxis": {"title": "Deaths per infected (CFR)", "hoverformat": ".3f"},
            "margin": {"l": 0, "r": 0},
        }
    )
    for country in countries_to_plot:
        data = (deaths[country] / infected[country]).dropna()
        fig.add_trace(
            go.Scatter(x=data.index, y=data.values, name=country, mode="lines")
        )
    return fig
