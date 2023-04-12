import backtrader as bt

class MyStrategy(bt.Strategy):
    def __init__(self):
        # Initialize indicators and other variables
        self.sma = bt.indicators.SMA(self.data.close, period=20)
        self.bbands = bt.indicators.BollingerBands(self.data.close, period=20)
        self.atr = bt.indicators.ATR(self.data, period=14)
        self.trade_size = 20
        self.stop_loss_percentage = 2
        self.take_profit_percentage = 4
        
    def next(self):
        # Check for buy signal at support level
        if self.data.close[0] < self.sma[0] - self.bbands.lines.bot[0]:
            # Calculate trade parameters
            stop_loss_distance = self.data.close[0] * self.stop_loss_percentage / 100
            take_profit_distance = self.data.close[0] * self.take_profit_percentage / 100
            stop_loss = self.data.close[0] - stop_loss_distance
            take_profit = self.data.close[0] + take_profit_distance
            quantity = self.trade_size / self.data.close[0]
            
            # Place buy order with stop loss and take profit
            self.buy(size=quantity, exectype=bt.Order.StopLimit, price=self.data.close[0], valid=bt.Order.DAY, stopprice=stop_loss, limitprice=take_profit)
            
        # Check for sell signal at resistance level
        elif self.data.close[0] > self.sma[0] + self.bbands.lines.top[0]:
            # Calculate trade parameters
            stop_loss_distance = self.data.close[0] * self.stop_loss_percentage / 100
            take_profit_distance = self.data.close[0] * self.take_profit_percentage / 100
            stop_loss = self.data.close[0] + stop_loss_distance
            take_profit = self.data.close[0] - take_profit_distance
            quantity = self.trade_size / self.data.close[0]
            
            # Place sell order with stop loss and take profit
            self.sell(size=quantity, exectype=bt.Order.StopLimit, price=self.data.close[0], valid=bt.Order.DAY, stopprice=stop_loss, limitprice=take_profit)

# Create a cerebro instance and add the strategy
cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)

# Load historical data
data = bt.feeds.GenericCSVData(dataname='price_data.csv', dtformat='%Y-%m-%d %H:%M:%S', timeframe=bt.TimeFrame.Minutes, compression=60)

# Add the data to cerebro
cerebro.adddata(data)

# Set the initial account balance and leverage
cerebro.broker.setcash(10000)
cerebro.broker.setcommission(commission=0.001)
cerebro.broker.set_coc(True)
cerebro.addsizer(bt.sizers.FixedSize, stake=20)

# Run the backtest
results = cerebro.run()

# Print the final account balance
print(f"Final balance:
