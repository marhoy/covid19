"""Try to forecast the development..."""
from typing import Tuple

import numpy as np
import pandas as pd


def growth_rate_exp_decay(initial_rate: float, days_until_control: int) -> np.array:
    """Calculate future growth rates.

    The rates decays exponentially towards 1.0.

    Args:
        initial_rate (float): Inital growth rate.
        days_until_control (int): How long until we reach (close to) 1.0

    Returns:
        np.array: The future growth rates
    """
    time_constant = days_until_control / 4
    x = np.arange(0, time_constant * 6)
    y = (initial_rate - 1) * np.exp(-x / time_constant) + 1
    return y


def create_forecast(
    infected: pd.Series,
    day_of_control: int,
    forecast_start: int = -1,
    days_to_recover: int = 14,
    ratio_avg_days: int = 4,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Create forecast of timeseries.

    Args:
        infected (pd.Series): The initial timeseries.
        day_of_control (int): The day when growth rate should reach (close to) 1.0
        forecast_start (int, optional): The day to start forcasting.
                                        Defaults to -1 (last day).
        days_to_recover (int, optional): How many days it takes for a patien to
                                         recover. Defaults to 14.
        ratio_avg_days (int, optional): How many days to use for estimation of initial
                                        growth rate. Defaults to 4.

    Returns:
        3 Pandas Series: observed_data, forecast, being_ill
    """
    # The initial time series and when to start forecasting
    observed_data = infected.dropna()
    forecast_start = min(forecast_start, observed_data.index[-1] - 1)

    # Calculate the inital growth rate
    increase_ratio = observed_data / observed_data.shift(1)
    initial_ratio = increase_ratio.ewm(span=ratio_avg_days).mean().iloc[forecast_start]

    # What is the last day of observed data, and the value on that day.
    last_obs_value = observed_data.iloc[forecast_start]
    last_obs_day = observed_data.index[forecast_start]

    # Estimate future growth rates.
    growth_ratios = growth_rate_exp_decay(initial_ratio, day_of_control - last_obs_day)

    # The forecast starts when the observation ends
    forecast = pd.Series(
        index=np.arange(last_obs_day, last_obs_day + len(growth_ratios) + 1),
        data=last_obs_value * np.concatenate([np.array([1]), growth_ratios]).cumprod(),
    )

    # Calculate number of ill people (ignore deaths)
    combined = pd.concat([observed_data[: forecast.index[0]], forecast])
    being_ill = combined - combined.shift(days_to_recover).fillna(0)

    return observed_data, forecast.astype(int), being_ill.astype(int)
