"""Create the tab with infection data."""
import itertools
from typing import List

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.colors
import plotly.graph_objects as go
from dash.dependencies import Input, Output

import covid19.dash_app

from .dash_app import app
from .data import DAY_ZERO_START

tab_infected = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Select one or more countries"),
                            dcc.Dropdown(
                                id="infected-countries-selector",
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
                                id="infected-plot-options",
                                switch=True,
                            ),
                        ]
                    ),
                    md=6,
                ),
            ]
        ),
        dbc.Row([dbc.Col(dcc.Graph(id="infected-in-total-figure"), md=12)]),
        dbc.Row([dbc.Col(dcc.Graph(id="infected-per-day-figure"), md=12)]),
        html.H2("Interactive map showing world status", className="mt-4 mb-4"),
        dbc.Row(dbc.Col(dcc.Graph(id="infected-map"), md=12, className="mb-4")),
        dbc.Row(
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Label(
                            "Select date. The labels are week numbers in 2020,"
                            " with the mark on the Monday of that week."
                        ),
                        html.Div(id="infected-map-slider-div"),
                    ]
                ),
                md=12,
            )
        ),
    ]
)


@app.callback(
    Output("infected-map-slider-div", "children"),
    [Input("interval-component", "n_intervals")],
)
def infected_map_slider_div_children(*_) -> dcc.Slider:
    """Create the slider for date-selection of map data."""
    slider = dcc.Slider(
        id="infected-map-date",
        min=0,
        max=len(covid19.dash_app.infected_raw) - 1,
        step=1,
        value=len(covid19.dash_app.infected_raw) - 1,
        marks={
            covid19.dash_app.infected_raw.index.get_loc(date): f"{date.week}"
            for date in pd.date_range(
                start=covid19.dash_app.infected_raw.index[0],
                end=covid19.dash_app.infected_raw.index[-1],
                freq="W-MON",
            )
        },
    )
    return [slider]


@app.callback(
    Output("infected-countries-selector", "options"),
    [Input("interval-component", "n_intervals")],
)
def infected_countries_selector_options(*_) -> List[dict]:
    """Scheduled update of the options of the country-selector."""
    return covid19.dash_app.all_countries


@app.callback(
    Output("infected-in-total-figure", "figure"),
    [
        Input("infected-countries-selector", "value"),
        Input("infected-plot-options", "value"),
    ],
)
def infected_in_total_figure(
    countries_to_plot: List[str], plot_options: List[str]
) -> go.Figure:
    """Update the infected-per-pop figure when the input changes."""
    # Handle plot options
    if "log_scale" in plot_options:
        y_axis_type = "log"
    else:
        y_axis_type = "linear"

    if "per_pop_size" in plot_options:
        fig_title = "Infected in total per 100k population"
        y_axis_title = "Infected per 100k"
    else:
        fig_title = "Infected people in total"
        y_axis_title = "Infected total"

    infected = covid19.dash_app.infected
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
                "hoverformat": ",.0f",
            },
            "hovermode": "x",
            "margin": {"l": 0, "r": 0},
        }
    )
    for country in countries_to_plot:
        if "per_pop_size" in plot_options:
            data = (
                infected[country].dropna()
                / population.loc[country, "Population"]
                * 100_000
            )
        else:
            data = infected[country].dropna()

        fig.add_trace(
            go.Scatter(x=data.index, y=data.values, name=country, mode="lines")
        )

    return fig


@app.callback(
    Output("infected-per-day-figure", "figure"),
    [
        Input("infected-countries-selector", "value"),
        Input("infected-plot-options", "value"),
    ],
)
def infected_per_day_figure(
    countries_to_plot: List[str], plot_options: List[str]
) -> go.Figure:
    """Plot number of infected people per day."""
    # Handle plot options
    if "log_scale" in plot_options:
        y_axis_type = "log"
    else:
        y_axis_type = "linear"

    if "per_pop_size" in plot_options:
        fig_title = "New infections per day per 100k population"
        y_axis_title = "Infections per day per 100k population"
    else:
        fig_title = "New infections per day"
        y_axis_title = "Infections per day"

    # Get data
    infected_per_day = covid19.dash_app.infected_raw.diff()
    population = covid19.dash_app.population

    fig = go.Figure(
        layout={
            "title": fig_title,
            "xaxis": {"title": "Date"},
            "yaxis": {
                "title": y_axis_title,
                "type": y_axis_type,
                "hoverformat": ",.0f",
            },
            "hovermode": "x",
            "margin": {"l": 0, "r": 0},
            "legend": {"tracegroupgap": 0},
        }
    )

    for country, color in zip(
        countries_to_plot, itertools.cycle(plotly.colors.qualitative.Plotly)
    ):
        if "per_pop_size" in plot_options:
            data = (
                infected_per_day[country]
                / population.loc[country, "Population"]
                * 100_000
            )
        else:
            data = infected_per_day[country]

        points = data  # .replace(0, pd.NA)
        line = data.rolling(window=pd.Timedelta("7days")).mean()

        fig.add_trace(
            go.Scatter(
                x=points.index,
                y=points.values,
                name=country,
                legendgroup=country,
                showlegend=False,
                hoverinfo="none",
                mode="markers",
                marker=go.scatter.Marker(color=color, size=3),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=line.index,
                y=line.values,
                name=country,
                legendgroup=country,
                hovertemplate="Average last week: %{y}",
                line=go.scatter.Line(color=color),
            )
        )

    return fig


@app.callback(Output("infected-map", "figure"), [Input("infected-map-date", "value")])
def infected_map_figure(idx: int) -> go.Figure:
    """When the date-slider-value changes, update the map."""
    infected_raw = covid19.dash_app.infected_raw
    population = covid19.dash_app.population
    inf_at_date = infected_raw.iloc[idx]
    inf_at_date = inf_at_date[round(inf_at_date) > 0]

    inf_at_date.name = "Infected"
    df = pd.concat([population, inf_at_date], axis=1, join="inner")
    df["Inf/Pop"] = df["Infected"] / df["Population"] * 100_000

    df["text"] = (
        "<b>"
        + df["Country"]
        + "</b><br><br>Total infected: "
        + df["Infected"].apply(lambda x: f"{x:,.0f}")
        + "<br>Population: "
        + df["Population"].apply(lambda x: f"{x:,.0f}")
        + "<br>Inf. per pop.: "
        + df["Inf/Pop"].apply(lambda x: f"{x:,.1f}")
    )

    fig = go.Figure(
        data=go.Choropleth(
            locations=df["ISO3"],
            z=df["Inf/Pop"].round(decimals=0),
            zmax=100,
            zmin=0,
            text=df["text"],
            hovertemplate="%{text}<extra></extra>",
            colorscale="Reds",
            marker_line_color="darkgray",
            marker_line_width=0.5,
        ),
        layout={
            "title": "COVID-19 Confirmed infected per 100.000 population",
            "margin": {"l": 0, "r": 0, "b": 10},
            "geo": {
                "showframe": False,
                "showcoastlines": False,
                "projection": {"scale": 1.2},
                "center": {"lon": 10, "lat": 20},
            },
        },
    )

    return fig
