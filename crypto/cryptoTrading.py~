""" 
    Fagner Nunes 07/2021
    trading bot unsing binance API
"""


import numpy as np
import pandas as pd 
import requests as r  
import os
import config
from binance.spot  import Spot
import logging
from binance.lib.utils import config_logging
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime


# import keys
BINANCE_KEY= config.BINANCE_KEY
BINANCE_SECRET_KEY = config.BINANCE_SECRET_KEY

#creates client obj
client = Spot(key=BINANCE_KEY,secret = BINANCE_SECRET_KEY)

# gets data from binance
data = r.get('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=500').json()

#colum in dataframe
my_columns = [

            "open-time",
            "open",
            "high",
            "low",
            "close",
            "EMA9",
            "EMA6",
            "EMA3",
            "WMA",
            "BUY",
            "SELL",
            "ATR"
            

        ]

# creates data frame
graph =  pd.DataFrame(columns = my_columns)


# creates a NaN to avoid errors  
NaN = np.nan
# populates dataframe
for candle in data:
    
    graph = graph.append(
            pd.Series([
                datetime.datetime.utcfromtimestamp(candle[0]/1000),
                candle[1],
                float(candle[2]),
                float(candle[3]),
                float(candle[4]),
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                NaN,
               NaN,
               NaN
                ],
                    index=my_columns
                ),
            ignore_index = True

            )

# this creates an array with integers 1 to 10 included    
weights = np.arange(1,11)

# calculating the wma 10
"""

A lambda function is a small anonymous function. 
A lambda function can take any number of arguments, but can only have one expression.
lambda arguments : expression

.apply() lets us create and pass any custum function to a ROLLING window

.dot product of two arrays.
"""
wma10 = graph['close'].rolling(10).apply(lambda prices: np.dot(prices, weights)/weights.sum(),raw = True)

graph['WMA'] = np.round(wma10, decimals = 3)


# calculating EMA
"""
A 10 day ema has a smoothingFactor/alfa = 2/(10+1) whichs is aprox 0.1818
"""
ema9 = graph['close'].ewm(span=9).mean()
ema6 = graph['close'].ewm(span=6).mean()
ema3 = graph['close'].ewm(span=3).mean()


high_low = graph['high'] - graph['low']
high_cp = np.abs(graph['high'] - graph['close'].shift())
low_cp = np.abs(graph['low'] - graph['close'].shift())
df = pd.concat([high_low,high_cp,low_cp],axis=1)
true_range = np.max(df, axis = 1)
atr = true_range.rolling(14).mean()
graph['ATR'] = atr

#adding ema to dataframe
graph['EMA9'] = np.round(ema9, decimals = 3)
graph['EMA6'] = np.round(ema6, decimals = 3)
graph['EMA3'] = np.round(ema3, decimals = 3)


# global variables 
position = False
stop_loss = 0
profit = 0
portfolio = 100
starting_portfolio = portfolio
shares = 0

# function that prints change in portfolio
def getPortfolio(v1,v2):
    percentile = ((v2-v1)/v1)*100
    print(f"profit: {percentile}%")

""" ATR average of the last 14 candles (1.5 to 1)"""
# algorithm to decide whent to buy and when to sell shares
for row in graph.index:
    
    EMA3 = graph.loc[row,'EMA3']
    EMA6 = graph.loc[row,'EMA6']
    EMA9 = graph.loc[row,'EMA9']
    price = graph.loc[row,'close']
    time =  graph.loc[row, 'open-time']
    
    if EMA3 > EMA6 and EMA3 > EMA9 and position==False:
        stop_loss = price - (price*(0.6/100))
        profit = price + (price*(0.86/100))        
        shares  = portfolio/price
        portfolio = 0
        graph.loc[row,"BUY"] = price
        position = True
        
    if EMA3 < EMA6 and EMA3 < EMA9 and position==True:
        graph.loc[row,"SELL"] = price
        portfolio = shares*price
        position = False
        
        print(f"portifolio {portfolio} at {time}")

getPortfolio(starting_portfolio,portfolio)
print(graph['ATR'],graph['open-time'])
#ploting graph
"""plot1 =plt.figure(1)
plt.plot(graph['open-time'],graph['close'],label = "Price",zorder=1)
plt.plot(graph['open-time'],graph['EMA9'], label= "ema9",zorder=1)
plt.plot(graph['open-time'],graph['EMA6'], label= "ema6", zorder=1)
plt.plot(graph['open-time'],graph['EMA3'], label= "ema3",zorder=1)

plot2= plt.figure(2)
plt.plot(graph['open-time'],graph['close'],label = "Price",zorder=1)
plt.scatter(graph['open-time'],graph['BUY'],label="buy")
plt.scatter(graph['open-time'],graph['SELL'],label="sell")        

plot3 = plt.figure(3)
plt.plot(graph['open-time'],graph['close'],label = "Price",zorder=1)
plt.plot(graph['open-time'],graph['ATR'],label = "ATR",zorder=1)

plt.xlabel("time")
plt.ylabel("price")
plt.legend()


plt.show()"""
