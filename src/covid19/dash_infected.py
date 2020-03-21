import covid19.data
import dash.dependencies
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go

from .dash_app import app, DROPDOWN_SELECTED_COUNTRIES, DROPDOWN_COUNTRIES_OPTIONS
from .data import DAY_ZERO_START

infected, deaths, population = covid19.data.get_shifted_data()
inf_per_pop = infected / population.loc[infected.columns, "Population"] * 100_000


def create_infected_map():
    inf_last = infected.ffill().iloc[-1]
    inf_last.name = "Infected"
    df = pd.concat([population, inf_last], axis=1, join="inner")
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
                "lat": 40,
            }
        },
        margin=dict(t=30, b=10, l=0, r=0),
    )
    return fig


tab_infected = html.Div([
    dbc.Row([
        dbc.Col(dbc.FormGroup([
            dbc.Label("Select one or more countries"),
            dcc.Dropdown(
                id="infected-countries-selector",
                options=DROPDOWN_COUNTRIES_OPTIONS,
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
        dbc.Col(dcc.Graph(id='infected-figure'), md=12)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(
            id='infected-map',
            figure=create_infected_map()
        ), md=12, className="mb-4")
    ]),

])


@app.callback(
    dash.dependencies.Output("infected-figure", "figure"),
    [dash.dependencies.Input("infected-countries-selector", "value"),
     dash.dependencies.Input("infected-plot-scale", "value")])
def create_infected_plot(countries_to_plot, y_axis_type):
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
