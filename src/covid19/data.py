import pandas as pd
from importlib import resources


DATA_SOURCE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
DAY_ZERO_START = 20


def get_covid():
    covid = pd.read_csv(DATA_SOURCE).groupby("Country/Region").sum()
    covid.index.name = "Country"
    covid = covid.rename({
        "US": "United States",
        "Korea, South": "South Korea",
        "Congo (Kinshasa)": "Congo",
        "Taiwan*": "Taiwan",
        "North Macedonia": "Macedonia",
        "Czechia": "Czech Republic",
    })
    covid = covid.drop(["Lat", "Long"], axis=1).T
    covid = covid.reset_index(drop=True)
    covid.index.name = "Day"
    return covid


def get_population():
    with resources.path("covid19.resources", "world_population.csv") as file:
        countries = pd.read_csv(file)
    countries["pop2020"] *= 1000
    countries["name"] = countries["name"].replace({
        "DR Congo": "Congo"
    })
    countries.index = countries["name"]
    countries.index.name = "Country"
    countries = countries.drop(countries.columns.difference(["pop2020", "area"]), axis=1)
    countries = countries.rename({
        "pop2020": "Population",
        "area": "Area"
    }, axis=1)
    countries["Density"] = countries["Population"] / countries["Area"]
    return countries


def shifted_data():
    covid = get_covid()
    countries = get_population()

    counts = []
    per_pop = []
    per_area = []
    per_dens = []
    for col in covid.columns:
        if col not in countries.index:
            # Skip countries where we don't have population data
            continue
        day_zero = covid[col].gt(DAY_ZERO_START)
        if not day_zero.any():
            # Skip countries that haven't passed DAY_ZERO_START people
            continue
        day_zero_idx = day_zero.idxmax()
        count = covid[col].loc[day_zero_idx:].reset_index(drop=True)
        if len(count.dropna()) < 5:
            # If a country has less than 5 days of history, skip it
            continue
        counts.append(count)
        per_pop.append(count / countries.loc[col, "Population"]*100_000)
        per_area.append(count / countries.loc[col, "Area"])
        per_dens.append(count / countries.loc[col, "Density"])

    counts = pd.DataFrame(counts).T
    per_pop = pd.DataFrame(per_pop).T
    per_area = pd.DataFrame(per_area).T
    per_dens = pd.DataFrame(per_dens).T

    return counts, per_pop, per_dens
