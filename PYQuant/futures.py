import ccxt
import numpy as np
import pandas as pd
from ta.volatility import BollingerBands
from ta.trend import EMA

# Define the trading parameters
symbol = 'BTC/USD'
timeframe = '4h'
leverage = 5
trade_size = 20
r_ratio = 2

# Define the exchange
exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET_KEY',
    'enableRateLimit': True
})

# Define the technical indicators
def get_indicators(data):
    # Calculate the moving averages
    data['ema20'] = EMA(data['close'], window=20)
    data['ema50'] = EMA(data['close'], window=50)
    
    # Calculate the Bollinger Bands
    indicator_bb = BollingerBands(close=data["close"], window=20, window_dev=2)
    data['bb_high_band'] = indicator_bb.bollinger_hband()
    data['bb_low_band'] = indicator_bb.bollinger_lband()
    
    return data

# Retrieve historical data
ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
data = data.set_index('timestamp')

# Calculate the indicators
data = get_indicators(data)

# Print the data
print(data.tail())   

# Define the trading logic
def trading_strategy(data):
    last_row = data.iloc[-1]
    prev_row = data.iloc[-2]
    
    # Check if the price is above the 20-day EMA and below the 50-day EMA
    if last_row['close'] > last_row['ema20'] and last_row['close'] < last_row['ema50']:
        
        # Check if the price is at or below the lower Bollinger Band
        if last_row['close'] <= last_row['bb_low_band']:
            # Calculate the stop loss and take profit levels
            stop_loss = last_row['close'] - (last_row['bb_low_band'] - last_row['close'])
            take_profit = last_row['close'] + r_ratio*(last_row['close'] - stop_loss)
            return ('buy', stop_loss, take_profit)
        
    # Check if the price is below the 20-day EMA and above the 50-day EMA
    elif last_row['close'] < last_row['ema20'] and last_row['close'] > last_row['ema50']:
        
        # Check if the price is at or above the upper Bollinger Band
        if last_row['close'] >= last_row['bb_high_band']:
            # Calculate the stop loss and take profit levels
            stop_loss = last_row['close'] + (last_row['close'] - last_row['bb_high_band'])
            take_profit = last_row['close'] - r_ratio*(stop_loss - last_row['close'])
            return ('sell', stop_loss, take_profit)
        
    # If none of the conditions are met, do not enter a trade
    return None

# Implement the trading strategy
trade = trading_strategy(data)

# Place a trade if the trading strategy returns a valid trade
if trade is not None:
    order_type, stop_loss, take_profit = trade
    
    # Determine the trade size based on the available account balance
    balance = exchange.fetch_balance()
    available_balance = balance['USD']['free'] * leverage
    trade_size = min(trade_size, available_balance)
    
    # Place the order
    if order_type == 'buy':
        order = exchange.create_limit_buy_order(symbol, trade_size, stop_loss)
        print('Placed buy order:', order)
        order = exchange.create_limit_sell_order(symbol, trade_size, take_profit)
        print('Placed take profit order:', order)
        order = exchange.create_stop_loss_order(symbol, trade_size, stop_loss)
        print('Placed stop loss order:', order)
    elif order_type == 'sell':
        order = exchange.create_limit_sell_order(symbol, trade_size, stop_loss)
        print('Placed sell order:', order)
        order = exchange.create_limit_buy_order(symbol, trade_size, take_profit)
        print('Placed take profit order:', order)
        order = exchange.create_stop_loss_order(symbol, trade_size, stop_loss)
        print('Placed stop loss order:', order) 

# Set the trading interval to 4 hours
interval = '4h'

# Start trading
while True:
    # Get the latest data
    data = get_data(symbol, interval, ma_periods, bb_periods)
    
    # Check if the data is valid
    if data is not None:
        # Implement the trading strategy
        trade = trading_strategy(data)
        
        # Place a trade if the trading strategy returns a valid trade
        if trade is not None:
            order_type, stop_loss, take_profit = trade
            
            # Determine the trade size based on the available account balance
            balance = exchange.fetch_balance()
            available_balance = balance['USD']['free'] * leverage
            trade_size = min(trade_size, available_balance)
            
            # Place the order
            if order_type == 'buy':
                order = exchange.create_limit_buy_order(symbol, trade_size, stop_loss)
                print('Placed buy order:', order)
                order = exchange.create_limit_sell_order(symbol, trade_size, take_profit)
                print('Placed take profit order:', order)
                order = exchange.create_stop_loss_order(symbol, trade_size, stop_loss)
                print('Placed stop loss order:', order)
            elif order_type == 'sell':
                order = exchange.create_limit_sell_order(symbol, trade_size, stop_loss)
                print('Placed sell order:', order)
                order = exchange.create_limit_buy_order(symbol, trade_size, take_profit)
                print('Placed take profit order:', order)
                order = exchange.create_stop_loss_order(symbol, trade_size, stop_loss)
                print('Placed stop loss order:', order)
                
    # Wait for the next trading interval
    time.sleep(4*60*60) # wait for 4 hours        