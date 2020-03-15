import covid19.data

import numpy as np
import pandas as pd


def growth_rate_exp_decay(initial_rate, days_until_control):
    x = np.arange(0, days_until_control*2)
    time_constant = days_until_control/4
    y = (initial_rate - 1)*np.exp(-x/time_constant) + 1
    return y


def growth_rate_linear_decay(initial_rate, days_until_control):
    rates = np.linspace(initial_rate, 1.0, days_until_control)
    return np.concatenate([rates, np.array([1]*days_until_control)])


def create_forecast(country, day_of_control, forecast_start=-1,
                    days_to_recover=14,
                    ratio_avg_days=4):
    counts, _, _ = covid19.data.shifted_data()

    observed_data = counts[country].dropna()
    forecast_start = min(forecast_start, observed_data.index[-1] - 1)

    increase_ratio = observed_data / observed_data.shift(1)
    last_obs_value = observed_data.iloc[forecast_start]
    last_obs_day = observed_data.index[forecast_start]
    initial_ratio = increase_ratio.ewm(span=ratio_avg_days).mean().iloc[forecast_start]

    growth_ratios = growth_rate_exp_decay(initial_ratio, day_of_control - last_obs_day)

    forecast = pd.Series(
        index=np.arange(last_obs_day, last_obs_day + len(growth_ratios) + 1),
        data=last_obs_value*np.concatenate([np.array([1]), growth_ratios]).cumprod()
    )

    combined = pd.concat([observed_data[:forecast.index[0]], forecast])
    being_ill = combined - combined.shift(days_to_recover).fillna(0)

    return observed_data, forecast, being_ill
