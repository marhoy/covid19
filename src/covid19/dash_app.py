"""Create and configure the Dash App."""
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output

import covid19.data

app = dash.Dash(
    external_stylesheets=[dbc.themes.CERULEAN],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
)
app.title = "Corona Dashboard"

DROPDOWN_SELECTED_COUNTRIES = [
    "Norway",
    "Denmark",
]

# We store all the data as global variables, and update them below
infected, deaths, population = covid19.data.get_shifted_data()
infected_raw = covid19.data.download_infected()
all_countries = [{"label": country, "value": country} for country in infected.columns]


# Periodically update the value of the global variables
@app.callback(
    Output("live-update-text", "children"),
    [Input("interval-component", "n_intervals")],
)
def live_update_text_children(*_):
    """Update global data and last-updated-text.

    Returns:
        HTML text with last-updated-info.
    """
    # We store all the data as global variables, and update them here
    global infected, deaths, population, infected_raw, all_countries
    infected, deaths, population = covid19.data.get_shifted_data()
    infected_raw = covid19.data.download_infected()
    all_countries = [
        {"label": country, "value": country} for country in infected.columns
    ]

    # Find elapsed time since last update
    data_timestamp = covid19.data.data_timestamp()
    now = pd.Timestamp.now(tz=data_timestamp.tz)
    since_update = (now - data_timestamp).round("10min")

    # Find time until next update
    if now.timetz() < covid19.data.DATA_UPDATE_TIME:
        update_date = now.date()
    else:
        update_date = now.date() + pd.Timedelta(1, "day")
    next_update = pd.Timestamp.combine(update_date, covid19.data.DATA_UPDATE_TIME)
    until_update = (next_update.astimezone(now.tz) - now).round("10min")

    # Return text about current and next update
    return html.P(
        f"Data updated {since_update.components.hours} hours and "
        f"{round(since_update.components.minutes/10)*10} minutes ago. "
        f"Next update expected in approx {until_update.components.hours} hours and "
        f"{round(until_update.components.minutes/10)*10} minutes."
    )
