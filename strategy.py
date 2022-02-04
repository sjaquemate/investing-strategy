from typing import Optional

import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import yfinance as yf
import numpy as np
from dataclasses import dataclass
import yahoo_fin.stock_info as si


# def get_historic_price(ticker, period='1000y'):
#     return yf.Ticker(ticker).history(period=period)#['Open']
#
#


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
    while subinterval.end < interval.end:
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


def calculate_strategy_distribution(data, interval, strategy_fn,
                           buy_period, strategy_duration):
    subintervals = split_into_subintervals(interval, strategy_duration)
    gains = []
    for subinterval in subintervals:
        prices = select_periodic_data(data, subinterval, buy_period)
        gain = strategy_fn(prices)
        gains.append(((subinterval.begin, subinterval.end), gain))

    gains = pd.DataFrame(gains, columns=['interval', 'gain']).set_index('interval')
    yearly = gains ** (1 / strategy_duration.years)

    return gains


def lump_sum_gain(data):
    return data[-1] / data[0]


def dca_gain(data):
    return len(data) * data[-1] / sum(data)


class Investing:

    def __init__(self):
        self.stock: Optional[Stock] = None
        self.interval = None

    def set_interval(self, begin, end):
        self.interval = Interval(begin, end)

    def set_ticker(self, ticker):
        if self.stock is not None and ticker == self.stock.ticker:
            return

        self.stock = Stock.from_ticker(ticker)

    def get_timeseries(self) -> pd.Series:
        return self.stock.monthly_price

    def calculate_distribution(self, strategy_fn):
        return calculate_strategy_distribution(self.stock.monthly_price, self.interval, strategy_fn,
                                               buy_period=relativedelta(months=1),
                                               strategy_duration=relativedelta(years=1))


def main():
    investing = Investing()
    investing.set_ticker('GE')
    investing.set_interval(datetime(1950, 1, 1), datetime(2010, 1, 1))

    print(investing.get_timeseries())
    print(investing.calculate_distribution(lump_sum_gain))

if __name__ == "__main__":
    main()