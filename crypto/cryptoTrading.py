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

# import keys
BINANCE_KEY= config.BINANCE_KEY
BINANCE_SECRET_KEY = config.BINANCE_SECRET_KEY

#creates client obj
client = Spot(key=BINANCE_KEY,secret = BINANCE_SECRET_KEY)

# gets data from binance
data = r.get('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=500').json()

#colum in dataframe
my_columns = [

            "open-time",
            "open",
            "high",
            "low",
            "close"

        ]

# creates data frame
graph =  pd.DataFrame(columns = my_columns)

#populates dataframe
for candle in data:
    graph = graph.append(
            pd.Series([
                float(candle[0]),
                candle[1],
                candle[2],
                candle[3],
                float(candle[4])
            
                ],
                    index=my_columns
                ),
            ignore_index = True

            )

#plots graph
graph.plot(y='close',x='open-time')
plt.show()
