import io
from datetime import timedelta
from importlib import resources
from typing import Tuple

import pandas as pd
import requests
import requests_cache

# Use caching of requests
requests_cache.install_cache(expire_after=timedelta(seconds=5))

INFECTED_SOURCE = r"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master" \
                  r"/csse_covid_19_data/csse_covid_19_time_series/time_series_19" \
                  r"-covid-Confirmed.csv"
DEATHS_SOURCE = r"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master" \
                r"/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid" \
                r"-Deaths.csv"

DAY_ZERO_START = 20


def download_infected():
    response = requests.get(INFECTED_SOURCE)
    buffer = io.StringIO(response.content.decode('UTF-8'))
    data = pd.read_csv(buffer)
    return preprocess_covid_dataframe(data)


def download_deaths():
    response = requests.get(DEATHS_SOURCE)
    buffer = io.StringIO(response.content.decode('UTF-8'))
    data = pd.read_csv(buffer)
    return preprocess_covid_dataframe(data)


def preprocess_covid_dataframe(data):
    # Treat Hubei in China as a separate country
    data.loc[data['Province/State'] == "Hubei", "Country/Region"] = "China - Hubei"
    data["Country/Region"] = data["Country/Region"].replace({
        "China": "China - Others"
    })

    data = data.groupby("Country/Region").sum()
    data.index.name = "Country"
    data = data.rename({
        "US": "United States",
        "Korea, South": "South Korea",
        "Congo (Kinshasa)": "Congo",
        "Taiwan*": "Taiwan",
        "North Macedonia": "Macedonia",
        "Czechia": "Czech Republic",
    })
    data = data.drop(["Lat", "Long"], axis=1).T
    data = data.reset_index(drop=True)
    data.index.name = "Day"
    return data


def get_population():
    with resources.path("covid19.resources", "world_population.csv") as file:
        countries = pd.read_csv(file)
    countries["pop2020"] *= 1000
    countries["name"] = countries["name"].replace({
        "DR Congo": "Congo"
    })
    countries.index = countries["name"]
    countries.index.name = "Country"
    countries = countries.drop(countries.columns.difference(["pop2020", "area"]),
                               axis=1)
    countries = countries.rename({
        "pop2020": "Population",
        "area": "Area"
    }, axis=1)

    # Add Hubei in China as a separate country
    countries.loc["China - Hubei", "Population"] = 58_500_000
    countries.loc["China - Hubei", "Area"] = 185_900
    countries.loc["China", "Population"] -= countries.loc["China - Hubei", "Population"]
    countries.loc["China", "Population"] -= countries.loc["China - Hubei", "Area"]
    countries = countries.rename({
        "China": "China - Others"
    })

    countries["Density"] = countries["Population"] / countries["Area"]
    return countries


def get_shifted_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    infected_all = download_infected()
    deaths_all = download_deaths()
    population = get_population()

    infected = []
    deaths = []
    for country in infected_all.columns:
        if country not in population.index:
            # Skip countries where we don't have population data
            continue
        day_zero_gt = infected_all[country].gt(DAY_ZERO_START)
        if not day_zero_gt.any():
            # Skip countries that haven't passed DAY_ZERO_START infected
            continue
        day_zero_idx = day_zero_gt.idxmax()
        s_infected = infected_all[country].loc[day_zero_idx:].reset_index(drop=True)
        s_deaths = deaths_all[country].loc[day_zero_idx:].reset_index(drop=True)
        if len(s_infected.dropna()) < 5:
            # If a country has less than 5 days of history, skip it
            continue
        infected.append(s_infected)
        deaths.append(s_deaths)

    # Transform list of Series into DataFrames
    infected = pd.DataFrame(infected).T
    deaths = pd.DataFrame(deaths).T

    # # Infected per population
    # inf_per_pop = pd.DataFrame(
    #     [infected[country] / population.loc[country, "Population"] for country in
    #      infected]).T
    # inf_per_pop *= 100_000
    #
    # # Dead per population
    # dea_per_pop = pd.DataFrame(
    #     [deaths[country] / population.loc[country, "Population"] for country in
    #      deaths]).T
    # dea_per_pop *= 100_000

    return infected, deaths, population
