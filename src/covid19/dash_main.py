import covid19.dash_deaths
import covid19.dash_forecast
import covid19.dash_infected
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .dash_app import app
from .dash_footer import footer

# The layout is divided in tabs
app.layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            [
                # This timer component is used to trigger automatic updating
                dcc.Interval(
                    id="interval-component",
                    interval=600 * 1000,  # 10 minutes
                    n_intervals=0,
                ),
                # This component is used to store/sync the value of the dropdown menus
                dcc.Store(
                    id="multiple-countries-selector-store",
                    data=covid19.dash_app.DROPDOWN_SELECTED_COUNTRIES,
                ),
                html.H1(
                    "COVID-19: Current status and possible future",
                    className="mt-4 mb-4",
                ),
                html.Div(id="live-update-text"),
                dcc.Tabs(
                    id="tabs",
                    value="tab-infected",
                    className="mb-4",
                    children=[
                        dcc.Tab(
                            label="Infected",
                            value="tab-infected",
                            className="h3",
                            selected_className="bg-primary",
                            children=[covid19.dash_infected.tab_infected],
                        ),
                        dcc.Tab(
                            label="Deaths",
                            value="tab-deaths",
                            className="h3",
                            selected_className="bg-primary",
                            children=[covid19.dash_deaths.tab_deaths],
                        ),
                        dcc.Tab(
                            label="Forecast",
                            value="tab-forecast",
                            className="h3",
                            selected_className="bg-primary",
                            children=[covid19.dash_forecast.tab_forecast],
                        ),
                    ],
                ),
                footer,
            ]
        )
    )
)

server = app.server


# When one of the dropdown menus changes, store the value
@app.callback(
    Output("multiple-countries-selector-store", "data"),
    [
        Input("infected-countries-selector", "value"),
        Input("deaths-countries-selector", "value"),
    ],
    [State("tabs", "value")],
)
def store_dropdown_value(infected_selected, deaths_selected, tab):
    if tab == "tab-infected":
        return infected_selected
    elif tab == "tab-deaths":
        return deaths_selected
    else:
        raise PreventUpdate


# Update the value of the dropdown menus when changing tab
@app.callback(
    [
        Output("infected-countries-selector", "value"),
        Output("deaths-countries-selector", "value"),
    ],
    [Input("tabs", "value")],
    [State("multiple-countries-selector-store", "data")],
)
def synchronize_dropdowns(tab, store):
    return store, store
