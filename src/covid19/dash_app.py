import covid19.data
import dash
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN],
                meta_tags=[
                    {'name': 'viewport',
                     'content': 'width=device-width, initial-scale=1'}
                ],
                suppress_callback_exceptions=True)
app.title = "Corona Dashboard"


infected, deaths, population = covid19.data.get_shifted_data()
countries = infected.columns

DROPDOWN_SELECTED_COUNTRIES = [
    "Norway", "Sweden", "Denmark", "Italy", "Spain",
    "Germany", "France", "United Kingdom", "China - Hubei"
]

DROPDOWN_COUNTRIES_OPTIONS = [
    {"label": country, "value": country} for country in countries
]
