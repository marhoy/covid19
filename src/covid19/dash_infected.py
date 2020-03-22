import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

import covid19.dash_app

from .dash_app import DROPDOWN_SELECTED_COUNTRIES, app
from .data import DAY_ZERO_START

tab_infected = html.Div([
    html.H2("Compare development in different countries"),
    dbc.Row([
        dbc.Col(dbc.FormGroup([
            dbc.Label("Select one or more countries"),
            dcc.Dropdown(
                id="infected-countries-selector",
                value=DROPDOWN_SELECTED_COUNTRIES,
                multi=True,
                clearable=False)
        ]), md=6),

        dbc.Col(dbc.FormGroup([
            dbc.Label("Select plot scale"),
            dbc.RadioItems(
                id="infected-plot-scale",
                options=[
                    {"value": "linear", "label": "Linear"},
                    {"value": "log", "label": "Logarithmic"},
                ],
                value='linear',
            )
        ]), md=6)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='infected-figure'), md=12, className="mb-4")
    ]),


    html.H2("Interactive map showing world status", className="mt-4 mb-4"),

    dbc.Row(dbc.Col(
        dcc.Graph(id='infected-map'),
        md=12, className="mb-4")
    ),
    dbc.Row(dbc.Col(
        dbc.FormGroup([
            dbc.Label("Select date. The labels are week numbers in 2020, with the "
                      "mark on the Monday of that week."),
            dcc.Slider(
                id="infected-map-date",
                min=0,
                max=len(covid19.dash_app.infected_raw) - 1,
                step=1,
                value=len(covid19.dash_app.infected_raw) - 1,
                marks={
                    covid19.dash_app.infected_raw.index.get_loc(date): f"{date.week}"
                    for date in pd.date_range(
                        start=covid19.dash_app.infected_raw.index[0],
                        end=covid19.dash_app.infected_raw.index[-1], freq="W-MON")
                    }
            )
        ]), md=6)
    )

])


@app.callback(Output("infected-countries-selector", "options"),
              [Input("infected-countries-selector", "value")])
def get_all_countries(*_):
    return covid19.dash_app.all_countries


@app.callback(
    Output("infected-figure", "figure"),
    [Input("infected-countries-selector", "value"),
     Input("infected-plot-scale", "value")])
def create_infected_plot(countries_to_plot, y_axis_type):
    infected = covid19.dash_app.infected
    population = covid19.dash_app.population
    inf_per_pop = infected / population.loc[infected.columns, "Population"] * 100_000

    fig = go.Figure(
        layout={
            "title": "Confirmed infected per population size",
            "xaxis": {
                "title":
                    f"Days since more that {DAY_ZERO_START} people confirmed infected"
            },
            "yaxis": {
                "title":
                    f"Confirmed infected per 100.000 population",
                "type": y_axis_type
            },
            "margin": dict(t=30, b=30, l=10, r=10)
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


@app.callback(Output("infected-map", "figure"),
              [Input("infected-map-date", "value")])
def create_infected_map(idx):
    infected_raw = covid19.dash_app.infected_raw
    population = covid19.dash_app.population
    inf_at_date = infected_raw.iloc[idx]
    inf_at_date = inf_at_date[round(inf_at_date) > 0]

    inf_at_date.name = "Infected"
    df = pd.concat([population, inf_at_date], axis=1, join="inner")
    df["Inf/Pop"] = df["Infected"] / df["Population"] * 100_000

    fig = go.Figure(data=go.Choropleth(
        locations=df["ISO3"],
        z=round(df["Inf/Pop"]),
        zmax=50,
        zmin=0,
        text=df["Country"],
        colorscale="Reds",
        marker_line_color="darkgray",
        marker_line_width=0.5,
    ))

    fig.update_layout(
        title_text='COVID-19 Confirmed infected per 100.000 population',
        geo={
            "showframe": False,
            "showcoastlines": False,
            "projection": {
                "scale": 1.2,
            },
            "center": {
                "lon": 10,
                "lat": 20,
            }
        },
        margin=dict(t=30, b=10, l=0, r=0),
    )
    return fig
