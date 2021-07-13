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
            "EMA",
            "WMA"

        ]

# creates data frame
graph =  pd.DataFrame(columns = my_columns)


 

# populates dataframe
for candle in data:
    graph = graph.append(
            pd.Series([
                float(candle[0]),
                candle[1],
                candle[2],
                candle[3],
                float(candle[4]),
                'na',
                'na'            
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
graph['EMA'] = np.round(ema9, decimals = 3)
plt.plot(graph['close'],label = "Price")
plt.plot(graph['EMA'], label= "ema9")

plt.xlabel("time")
plt.ylabel("price")
plt.legend()
#plots graph
#graph.plot(y='EMA',x='open-time')
#graph.plot(y="close",x='open-time')
plt.show()
