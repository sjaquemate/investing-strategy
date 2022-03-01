from typing import Optional

import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
from dataclasses import dataclass
import yahoo_fin.stock_info as si
import plotly.express as px


# def get_historic_price(ticker, period='1000y'):
#     return yf.Ticker(ticker).history(period=period)#['Open']


def select_periodic_data(data, interval, period):
    dates = []
    date = interval.begin
    while date < interval.end:
        dates.append(date)
        date += period

    closest_indices = data.index.searchsorted(dates)
    return data.iloc[closest_indices]


def get_monthly_price(ticker):  # todo get earlier prices
     return si.get_data(ticker, start_date=datetime(1900, 1, 1),
                       interval="1mo")['open'][:-1]  # monthly price without the last date


@dataclass
class Interval:
    begin: datetime
    end: datetime


def split_into_subintervals(interval: Interval, duration: relativedelta,
                           increment=relativedelta(months=1)):
    subintervals = []
    subinterval = Interval(interval.begin, interval.begin + duration)
    while subinterval.end <= interval.end:
        subintervals.append(subinterval)
        subinterval = Interval(subinterval.begin + increment,
                               subinterval.end + increment)

    return subintervals


@dataclass
class Stock:
    ticker: str
    monthly_price: pd.DataFrame()

    @classmethod
    def from_ticker(cls, ticker, interval=Interval(datetime(1990, 1, 1), datetime.now())):
        # historic_price = get_historic_price(ticker)
        # monthly_price = select_periodic_data(historic_price, interval, relativedelta(months=1))
        monthly_price = get_monthly_price(ticker)
        return cls(ticker, monthly_price)


def calculate_strategy_gains(data, interval, strategy_fn,
                             buy_period, investing_duration):
    subintervals = split_into_subintervals(interval, investing_duration)
    gains = []
    for subinterval in subintervals:
        prices = select_periodic_data(data, subinterval, buy_period)
        gain = strategy_fn(prices)
        gains.append( ((subinterval.begin, subinterval.end), gain) )

    df_gains = pd.DataFrame(gains, columns=['interval', 'gains_total']).set_index('interval')
    df_gains['gains_yearly'] = df_gains['gains_total'] ** (1 / investing_duration.years)
    return df_gains


def lump_sum_gain(data):
    return data[-1] / data[0]


def dca_gain(data):
    return len(data) * data[-1] / sum(data)


class Investing:

    def __init__(self):
        self.stock: Optional[Stock] = None
        self.interval = None

    def set_interval_years(self, begin, end):
        self.interval = Interval(datetime(begin, 1, 1), datetime(end, 1, 1))

    def get_interval_dates(self) -> (datetime, datetime):
        return self.interval.begin, self.interval.end

    def set_ticker(self, ticker):
        if self.stock is not None and ticker == self.stock.ticker:
            return

        self.stock = Stock.from_ticker(ticker)

    def get_timeseries(self) -> pd.Series:
        return self.stock.monthly_price

    def calculate_distribution(self, strategy_fn, investing_duration_years):
        return calculate_strategy_gains(self.stock.monthly_price, self.interval, strategy_fn,
                                        buy_period=relativedelta(months=1),
                                        investing_duration=relativedelta(years=investing_duration_years))


def main():
    investing = Investing()
    investing.set_ticker('GE')
    investing.set_interval_years(1990, 2020)

    gains = investing.calculate_distribution(dca_gain)
    print(gains.head(2))
    fig = px.histogram(gains, x="gain")
    fig.update_layout(bargap=0.2)
    fig.show()

if __name__ == "__main__":
    main()