import ccxt
import talib
import numpy as np
import time

# Define the trading pair and interval
exchange = ccxt.binance()
symbol = 'BTC/USDT'
interval = '15m'

# Define the moving average period
ma_period = 50

# Define the Bollinger Bands parameters
bb_period = 20
bb_std = 2

# Define the trade amount
trade_amt = 10

# Run the trading bot
while True:
    # Get the historical klines
    klines = exchange.fetch_ohlcv(symbol=symbol, timeframe=interval, limit=100)

    # Extract the closing prices
    close_prices = [float(x[4]) for x in klines]

    # Calculate the moving average
    ma = talib.SMA(np.array(close_prices), ma_period)

    # Calculate the upper and lower Bollinger Bands
    upper_band, middle_band, lower_band = talib.BBANDS(np.array(close_prices), 
                                                       timeperiod=bb_period, 
                                                       nbdevup=bb_std, 
                                                       nbdevdn=bb_std, 
                                                       matype=talib.MA_Type.SMA)

    # Get the current price
    curr_price = exchange.fetch_ticker(symbol)['last']

    # Check if the current price is below the lower Bollinger Band
    if curr_price < lower_band[-1]:
        # Buy order
        try:
            order = exchange.create_market_buy_order(symbol=symbol, amount=trade_amt)
            print("BUY order executed")
            time.sleep(5) # Wait for the order to process
        except:
            print("BUY order failed")

    # Check if the current price is above the upper Bollinger Band
    elif curr_price > upper_band[-1]:
        # Sell order
        try:
            order = exchange.create_market_sell_order(symbol=symbol, amount=trade_amt)
            print("SELL order executed")
            time.sleep(5) # Wait for the order to process
        except:
            print("SELL order failed")

    # Wait for the next interval
    time.sleep(exchange.parse_timeframe(interval) * 60)
