""" 
    Fagner Nunes 07/2021
    trading bot using binance API
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
import queue
import threading

#import testnet keys
testkey = config.TEST_KEY
testSecret = config.TEST_SECRET_KEY

# import keys
BINANCE_KEY= config.BINANCE_KEY
BINANCE_SECRET_KEY = config.BINANCE_SECRET_KEY

#creates client obj
client = Spot(key=BINANCE_KEY,secret = BINANCE_SECRET_KEY)


# fuction to get market change in last 24h
def change24H():
    my_columns =  ["ticker","percentile",'volume']
    #url = 'https://api.binance.com/api/v1/ticker/24hr?'
    url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h'
    response =  r.get(url).json()
    market = pd.DataFrame(columns = my_columns)

    for data in response:
        market = market.append(
            pd.Series([
                data["symbol"],
                data["price_change_percentage_1h_in_currency"],
                data["total_volume"]

                ],
                    index=my_columns
                ),
            ignore_index = True

            )

    market.sort_values("percentile",ascending= False,inplace= True)
    symbol = market.iloc[0]
    
    return symbol['ticker']+"usdt"
 




# gets data from binance
def get_pastData(symbol, startTime):
    data = r.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=1000").json()
    return data 


def create_dataFrame(data_set, symbol):
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
            "ATR",
            "portfolio"

        ]

    # creates data frame
    graph =  pd.DataFrame(columns = my_columns)


    # creates a NaN to avoid errors  
    NaN = np.nan
    # populates dataframe
    for candle in data_set:
    
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
               NaN,
               NaN
            
                ],
                    index=my_columns
                ),
            ignore_index = True

            )
    return graph
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

def calcWMA(n):
    wma10 = graph['close'].rolling(n).apply(lambda prices: np.dot(prices, weights)/weights.sum(),raw = True)

    graph['WMA'] = np.round(wma10, decimals = 3)


# calculating EMA
"""
A 10 day ema has a smoothingFactor/alfa = 2/(10+1) whichs is aprox 0.1818
"""

def calc_ema(dataset,n):
    ema = dataset['close'].ewm(span=n).mean()
    return ema

#ema9 = graph['close'].ewm(span=9).mean()
#ema6 = graph['close'].ewm(span=6).mean()
#ema3 = graph['close'].ewm(span=3).mean()

def calculate_atr(DATA,n):
    high_low = DATA['high'] - DATA['low']
    high_cp= np.abs(DATA['high'] - DATA['close'].shift())
    low_cp = np.abs(DATA['low'] - DATA['close'].shift())
    dp = pd.concat([high_low,high_cp,low_cp],axis=1)
    true_range = np.max(dp,axis=1)
    atr = true_range.rolling(n).mean()
    return atr


# function that prints change in portfolio
def getPortfolio(v1,v2):
    percentile = ((v2-v1)/v1)*100
    print(f"profit: {percentile}%")

""" ATR average of the last 14 candles (1.5 to 1)"""

# algorithm to decide whent to buy and when to sell shares
def buy_sell(graph,port):
  
    # global variables 
    position = False    
    stop_loss = 0
    profit = 0
    portfolio = port
    starting_portfolio = portfolio
    shares = 0

    
    
    for row in graph.index[15:]:
        
        
        EMA3 = graph.loc[row,'EMA3']
        EMA6 = graph.loc[row,'EMA6']
        EMA9 = graph.loc[row,'EMA9']
        price = graph.loc[row,'close']
        time =  graph.loc[row, 'open-time']
        
        if EMA3 > EMA6 and EMA3 > EMA9 and position==False:
        
            stop_loss = price - (graph.loc[row,'ATR']*1.5)
            profit = price + (graph.loc[row,'ATR']*3)  
            shares  = portfolio/price
            portfolio = 0
            graph.loc[row,"BUY"] = price
            position = True 
        
        if  price>=profit and position==True or price <= stop_loss and position==True:
            graph.loc[row,"SELL"] = price
            portfolio = shares*price
            position = False
            graph.loc[row,"portfolio"] = portfolio

            
            #getPortfolio(starting_portfolio,portfolio)               
        
    return graph

#getPortfolio(starting_portfolio,portfolio)

#with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#    print(graph[['open-time','ATR']])

# function creating console
def console(q):
    
    # infinit loop
    while 1:
        # get input
        cmd = input("> ")
        q.put(cmd)

        #leave infinit loop
        if cmd == "quit":
            break
#actios
def simulation():
    #getting symbol
    symbol = input("enter symbol: ")


    #testing functions
    pastDATA = get_pastData(symbol,1222)
    graph = create_dataFrame(pastDATA,symbol)
    ema9 = calc_ema(graph,9)
    ema6 = calc_ema(graph,6)
    ema3 = calc_ema(graph,3)

    atr = calculate_atr(graph,14) 
    graph['ATR'] = atr
    #adding ema to dataframe
    graph['EMA9'] = np.round(ema9, decimals = 3)
    graph['EMA6'] = np.round(ema6, decimals = 3)
    graph['EMA3'] = np.round(ema3, decimals = 3)

    graph = buy_sell(graph,100)

    #ploting graph
    plot1 =plt.figure(1)
    plt.plot(graph['open-time'],graph['close'],label = "Price",zorder=1)
    plt.plot(graph['open-time'],graph['EMA9'], label= "ema9",zorder=1)
    plt.plot(graph['open-time'],graph['EMA6'], label= "ema6", zorder=1)
    plt.plot(graph['open-time'],graph['EMA3'], label= "ema3",zorder=1)

    plot2= plt.figure(2)
    plt.plot(graph['open-time'],graph['close'],label = "Price",zorder=1)
    plt.scatter(graph['open-time'],graph['BUY'],label="buy")
    plt.scatter(graph['open-time'],graph['SELL'],label="sell")        

    plot3 = plt.figure(3)
    plt.plot(graph["open-time"], graph['portfolio'], marker = 'o',label = "Portfolio")



    plt.xlabel("time")
    plt.ylabel("price")

    plt.legend()
    plt.show()


def foo():
    print("TESTINGG")

def invalid_input():
    print("invalid command :( ")
# main
def main():
    #actions connected to function
    cmd_actions = {'foo':foo,'simulation':simulation}

    cmd_queue =  queue.Queue()

    dj = threading.Thread(target = console, args = {cmd_queue})
    dj.start()

    while 1:
        cmd = cmd_queue.get()
        if cmd == 'quit':
            break
        action = cmd_actions.get(cmd, invalid_input)
        action()

main()
