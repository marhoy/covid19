import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import covid19.dash_deaths
import covid19.dash_forecast
import covid19.dash_infected

from .dash_app import app
from .dash_footer import footer

# The layout is divided in tabs
app.layout = dbc.Container(
    dbc.Row(dbc.Col(
        [
            html.H1("COVID-19: Current status and possible future",
                    className="mt-4 mb-4"),
            dcc.Interval(
                id='interval-component',
                interval=600*1000,  # 10 minutes
                n_intervals=0),
            html.Div(id="live-update-text"),
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="Infected",
                        tab_id="tab-infected",
                        labelClassName="h3 mb-0",
                    ),
                    dbc.Tab(
                        label="Deaths",
                        tab_id="tab-deaths",
                        labelClassName="h3 mb-0",
                    ),
                    dbc.Tab(
                        label="Forecast",
                        tab_id="tab-forecast",
                        labelClassName="h3 mb-0",
                    ),
                ],
                id="tabs",
                # active_tab="tab-infected",
                className="mb-4"
            ),
            html.Div(id="tabs-content"),

            footer
        ]
    ))
)

server = app.server


# This function activates the selected tab
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'active_tab')])
def tabs_content_children(tab):
    if tab == 'tab-infected':
        return covid19.dash_infected.tab_infected
    elif tab == 'tab-deaths':
        return covid19.dash_deaths.tab_deaths
    elif tab == 'tab-forecast':
        return covid19.dash_forecast.tab_forecast
