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
    # Rename some countries before we groupby and sum
    data["Country/Region"] = data["Country/Region"].replace({
        "Congo (Brazzaville)": "Congo",
        "Congo (Kinshasa)": "Congo",
    })

    # Append Hubei in China as a separate country
    hubei = data[data["Province/State"] == "Hubei"].copy()
    hubei.at[:, "Country/Region"] = "China - Hubei"
    data = data.append(hubei)

    # Sum over all Province/State within the same Country/Region
    data = data.groupby("Country/Region").sum()

    # Add the rest of China (minus Hubei) as a separate country
    china_others = data.loc["China"] - data.loc["China - Hubei"]
    china_others.name = "China - Others"
    data = data.append(china_others)

    # Rename some countries to match with the population data
    data = data.rename({
        "Bahamas, The": "Bahamas",
        "Cote d'Ivoire": "Côte d'Ivoire",
        "Gambia, The": "Gambia",
        "US": "United States of America",
        "Korea, South": "South Korea",
        "Taiwan*": "Taiwan",
        "North Macedonia": "Macedonia",
    })

    data = data.drop(["Lat", "Long"], axis=1).T
    data = data.reset_index(drop=True)
    data.index.name = "Day"
    data = data.sort_index()

    return data


def get_population():
    with resources.path("covid19.resources", "world_population.csv") as file:
        countries = pd.read_csv(file, index_col=False)

    # Simplify some country names
    countries["Country"] = countries["Country"].replace({
        "Bolivia (Plurinational State of)": "Bolivia",
        "Brunei Darussalam": "Brunei",
        "Iran (Islamic Republic of)": "Iran",
        "Republic of Korea": "South Korea",
        "Republic of Moldova": "Moldova",
        "North Macedonia": "Macedonia",
        "Russian Federation": "Russia",
        "China, Taiwan Province of China": "Taiwan",
        "United Republic of Tanzania": "Tanzania",
        "Venezuela (Bolivarian Republic of)": "Venezuela",
        "Viet Nam": "Vietnam"
    })
    countries.index = countries["Country"]

    # Add Hubei in China as a separate country
    countries.loc["China - Hubei", "Population"] = 58_500_000
    countries.loc["China - Hubei", "PopulationDensity"] = 58_500_000 / 185_900
    countries.loc["China - Others", "Population"] = \
        countries.loc["China", "Population"] - 58_500_000
    countries.loc["China - Others", "PopulationDensity"] = \
        countries.loc["China - Others", "Population"] / (9_597_000 - 185_900)

    countries = countries.sort_index()

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
