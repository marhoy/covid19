"""Create the tab with infection data."""
from typing import List

import covid19.dash_app
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

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
                            dbc.Label("Select plot scale"),
                            dbc.RadioItems(
                                id="infected-plot-scale",
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
        dbc.Row([dbc.Col(dcc.Graph(id="infected-per-pop-figure"), md=12)]),
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
                md=6,
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
    Output("infected-per-pop-figure", "figure"),
    [
        Input("infected-countries-selector", "value"),
        Input("infected-plot-scale", "value"),
    ],
)
def infected_per_pop_figure_figure(
    countries_to_plot: List[str], y_axis_type: str
) -> go.Figure:
    """Update the infected-per-pop figure when the input changes."""
    infected = covid19.dash_app.infected
    population = covid19.dash_app.population

    fig = go.Figure(
        layout={
            "title": "Infected per population size",
            "xaxis": {
                "title": f"Days since more that {DAY_ZERO_START}"
                f" people confirmed infected"
            },
            "yaxis": {
                "title": f"Infected per 100.000 population",
                "type": y_axis_type,
            },
        }
    )
    for country in countries_to_plot:
        data = (
            infected[country].dropna() / population.loc[country, "Population"] * 100_000
        )
        fig.add_trace(
            go.Scatter(x=data.index, y=data.values, name=country, mode="lines")
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
            z=round(df["Inf/Pop"]),
            zmax=100,
            zmin=0,
            text=df["text"],
            hovertemplate="%{text}<extra></extra>",
            colorscale="Reds",
            marker_line_color="darkgray",
            marker_line_width=0.5,
        )
    )

    fig.update_layout(
        title_text="COVID-19 Confirmed infected per 100.000 population",
        geo={
            "showframe": False,
            "showcoastlines": False,
            "projection": {"scale": 1.2},
            "center": {"lon": 10, "lat": 20},
        },
        margin=dict(t=80, b=10, l=0, r=0),  # noqa: E741
    )
    return fig
