import pandas as pd
import robin_stocks.robinhood as rh
import robin_stocks.helper as helper
import robin_stocks.urls as urls


class Trader():
    def __init__(self, stocks):
        self.stocks = stocks

        self.sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}
        self.run_time = 0  # for historical data
        # self.buffer = 0.005

        self.price_sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}

    def get_historical_prices(self, stock, span):
        span_interval = {'day': '5minute',
                         'week': '10minute',
                         'month': 'hour',
                         '3month': 'hour',
                         'year': 'day',
                         '5year': 'week'
                         }
        interval = span_interval[span]

        historical_data = rh.stocks.get_stock_historicals(
            stock, interval=interval, span=span, bounds='extended')

        data_frame = pd.DataFrame(historical_data)

        # format date column in data frame
        dates_times = pd.to_datetime(data_frame.loc[:, 'begins_at'])
        # grab and format close_prices
        close_prices = data_frame.loc[:, 'close_price'].astype('float')

        data_frame_price = pd.concat([close_prices, dates_times], axis=1)
        data_frame_price = data_frame_price.rename(
            columns={'close_price': stock})
        data_frame_price = data_frame_price.set_index('begins_at')

        return data_frame_price

    def get_sma(self, stock, data_frame_prices, window=12):
        # window=12 defines how far back we are looking in 5 minute intervals 12* 5 = 60 min4

        # get average for the past 12 prices
        sma = data_frame_prices.rolling(
            window=window, min_periods=window).mean()
        sma = round(float(sma[stock].iloc[-1]), 4)
        return sma

    def get_price_sma(self, price, sma):
        price_sma = round(price/sma, 4)
        return (price_sma)

    def trade_option(self, stock, price):
        # get new historical prices every 5 minutes
        if self.run_time % (5) == 0:
            data_frame_hist_prices = self.get_historical_prices(
                stock, span='day')
            self.sma_hour[stock] = self.get_sma(
                stock, data_frame_hist_prices[-12:], window=12)

        self.price_sma_hour[stock] = self.get_price_sma(
            price, self.sma_hour[stock])
        p_sma = self.price_sma_hour[stock]

        index_one = 'BUY' if self.price_sma_hour[stock] < (
            1.0) else 'SELL' if self.price_sma_hour[stock] > (1.0) else "NONE"

        # in future if we want to add indicators
        if index_one == 'BUY':
            trade = 'BUY'
        elif index_one == 'SELL':
            trade = 'SELL'
        else:
            trade = 'HOLD'

        return trade
