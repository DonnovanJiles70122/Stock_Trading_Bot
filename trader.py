import config
from trading_strategy import Trader

import robin_stocks.robinhood as rh
import datetime as dt
import time

# login function


def login(days):
    time_logged_in = 60*60*24*days
    rh.authentication.login(username=config.username,
                            password=config.password,
                            expiresIn=time_logged_in,
                            scope='internal',
                            by_sms=True,
                            store_session=True)


def logout():
    rh.authentication.logout()

# creating a list on stock tickers for price check


def get_stocks():
    stocks = list()
    stocks.append('FUBO')
    stocks.append('DNA')
    stocks.append('GRAB')
    stocks.append('SPCE')

    return stocks

# check if the market is open


def open_market():
    market = True
    time_now = dt.datetime.now().time()

    market_open = dt.time(9, 30, 0)
    market_close = dt.time(15, 45, 0)

    if time_now > market_open and time_now < market_close:
        market = True
    else:
        print('market is closed')

    return market


def get_cash():
    rh_cash = rh.account.build_user_profile()

    cash = float(rh_cash['cash'])
    equity = float(rh_cash['equity'])
    return (cash, equity)


if __name__ == "__main__":
    login(days=1)
    stocks = get_stocks()
    print(f'stocks: ', stocks)

    ts = Trader(stocks)

    while open_market():
        prices = rh.stocks.get_latest_price(stocks)
        cash, equity = get_cash()

        # get prices for all stocks in list
        for i, stock in enumerate(stocks):
            price = float(prices[i])
            data = ts.get_historical_prices(stock=stock, span='day')
            sma = ts.get_sma(
                stock=stock, data_frame_prices=data)

            p_sma = ts.get_price_sma(price=price, sma=sma)

            print(f'{stock} = ${price}\tsma : {sma}\tprice/sma : {p_sma}')

            trade = ts.trade_option(stock, price)
            print(f'trade : {trade}')

        time.sleep(30)

    logout()
