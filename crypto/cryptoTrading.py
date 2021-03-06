"""
    Fagner Nunes 07/2021
    trading bot using binance API
"""
import sys
import hmac
from urllib.parse import urlencode, urljoin
import hashlib
import numpy as np
import pandas as pd 
from pandas import ExcelWriter
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
import time
import logging
import websocket
import asyncio
import json
from binance.websocket.spot.websocket_client import SpotWebsocketClient as Client
from matplotlib.animation import FuncAnimation
import concurrent.futures
import multiprocessing as mp
from multiprocessing import freeze_support,Manager
from binance.error import ClientError
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from playsound import playsound
import ta
import talib  as pta

"""
    GETTING Arguments 
"""
args = sys.argv

#import testnet keys
testkey = config.TEST_KEY
testSecret = config.TEST_SECRET_KEY

# import keys
BINANCE_KEY= config.BINANCE_KEY
BINANCE_SECRET_KEY = config.BINANCE_SECRET_KEY

test_url = 'https://testnet.binance.vision'
#creates client obj
client = Spot(key=BINANCE_KEY,secret = BINANCE_SECRET_KEY)
#client = Spot(testkey, testSecret,base_url=test_url)

headers = {
    'X-MBX-APIKEY': testkey
}
plt.style.use('fivethirtyeight')

   #colum in dataframe
my_columns = [

            "open-time",
            "open",
            "high",
            "low",
            "close",
            "MACD",
            'EMA200',
            "EMA26",
            "EMA12",
            "EMA9",
            "EMA6",
            "EMA3",
            "WMA",
            "BUY",
            "SELL",
            "ATR",
            "portfolio",
            "signal",
            "support",
            "resistance",
            "benchmark",
            'rsi',
            'sarUP',
            'sarDOWN',
            'stoch'
        ]

def place_order(symbol,side,typee,quantity):
    symbol = symbol.upper()
    params = {    
    "symbol": symbol,
    "side": side,
    "type": typee,
    "quantity": quantity,
    }
    response = client.new_order(**params)
    return response

def cancel_all_open_orders(symbol):
    orders = client.get_open_orders(symbol)
    for order in orders:
        response = client.cancel_order(symbol, orderId=order['orderId'])
        print("order canceled")

NaN = np.nan
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




def extended_pastData(symbol,interval,candles):
    symbol = symbol.upper()
    data = []
    i = int(candles / 1000)
    print(i)
    resp = r.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=1000").json()
    last = resp[1][0]
    #print(datetime.datetime.utcfromtimestamp(last/1000),  datetime.datetime.utcfromtimestamp(float(resp[-1][0])/1000),)
    data.extend(resp)
    for b in range(i-1):
        resp2 = r.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&endTime={last}&limit=1000").json()
        last = resp2[1][0]
        #print(datetime.datetime.utcfromtimestamp(last/1000),  datetime.datetime.utcfromtimestamp(float(resp2[-1][0])/1000),)
        data = resp2 + data
        
    print(len(data))
    return data
    

# gets data from binance
def get_pastData(symbol,interval):
    symbol =symbol.upper()
    data = r.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=350").json()
    return data 


def create_dataFrame(data_set):
 
    # creates data frame
    graph =  pd.DataFrame(columns = my_columns)


    # creates a NaN to avoid errors  
    NaN = np.nan
    # populates dataframe
    for candle in data_set:
    
        graph = graph.append(
            pd.Series([
                datetime.datetime.utcfromtimestamp(float(candle[0])/1000),
                candle[1],
                float(candle[2]),
                float(candle[3]),
                float(candle[4]),
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                'NA',
                'NA',
                'NA',
                NaN,
               NaN,
               NaN,
               NaN,
               NaN,
               NaN,
               NaN,NaN,NaN,NaN,NaN,NaN
            
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

def calc_macd(ema12,ema26):
    macd = []
    for i in range(len(ema12)):
        hold = ema12[i] - ema26[i]
        macd.append(hold)
    return macd

def is_support(df,i):  
  cond1 = df['close'][i] < df['close'][i-1]   
  cond2 = df['close'][i] < df['close'][i+1]   
  cond3 = df['close'][i+1] < df['close'][i+2]   
  cond4 = df['close'][i-1] < df['close'][i-2]  
  return (cond1 and cond2 and cond3 and cond4)

def is_resistance(df,i):  
  cond1 = df['close'][i] > df['close'][i-1]   
  cond2 = df['close'][i] > df['close'][i+1]   
  cond3 = df['close'][i+1] > df['close'][i+2]   
  cond4 = df['close'][i-1] > df['close'][i-2]  
  return (cond1 and cond2 and cond3 and cond4)

# to make sure the new level area does not exist already
def is_far_from_level(value, levels, df):    
  ave =  np.mean(df['High'] - df['Low'])    
  return np.sum([abs(value-level)<ave for _,level in levels])==0

# calculating EMA
"""
A 10 day ema has a smoothingFactor/alfa = 2/(10+1) whichs is aprox 0.1818
"""

def calc_ema(dataset,n):
    ema = dataset['close'].ewm(span=n,adjust = False, ignore_na=False).mean()
    return ema

#ema9 = graph['close'].ewm(span=9).mean()
#ema6 = graph['close'].ewm(span=6).mean()
#ema3 = graph['close'].ewm(span=3).mean()

def calc_change(new,old):
    change = ((new-old)/old)*100
    return change

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
    win = 0
    loose = 0
    buy = 0
    cycle = True
    fees = 0
    TSL =0
    count = 0
    looking = 0
    for row in graph.index[28:]:
        
        EMA3 = graph.loc[row,'EMA3']
        EMA6 = graph.loc[row,'EMA6']
        signal = graph.loc[row,'signal']
        EMA200 = graph.loc[row,'EMA200']
        price = graph.loc[row,'close']
        time =  graph.loc[row, 'open-time']
        macd =  graph.loc[row,'MACD']
        high = graph.loc[row,'high']
        low = graph.loc[row,'low'] 
        rsi = graph.loc[row,'rsi']
        sarUP = graph.loc[row,'sarUP']
        nan = np.nan
        stoch = graph.loc[row,'stoch']
        atr = graph.loc[row,'ATR'] 
        
        if signal > macd:
            cycle = True
         
        if position == True:
            count +=1
        """    if high  > graph.loc[row -1,'benchmark']:
                graph.loc[row,'benchmark'] = price
            else:
                graph.loc[row,'benchmark'] = graph.loc[row-1,'benchmark']
            #TSL = graph.loc[row,'benchmark'] - (graph.loc[row,'ATR']*2)
            TSL = graph.loc[row,'benchmark'] - (graph.loc[row,'benchmark']*0.01)
            print(graph.loc[row,'benchmark'])
        """
        if position == False:
            looking +=1
        if  position == False and rsi<0.10 and sarUP <  price  and cycle == True :           
            stop_loss = sarUP
            print(graph.loc[row,'open-time'],'sarUP',sarUP,'price',price, 'rsi',rsi,'hig',high,'low',low,'looking',looking)
            looking = 0
            profit = price + (price * 0.010) 
            #stop_loss = low -(price*0.01)
            #profit = price + (price*0.016)
            shares  = portfolio/price
            fees += portfolio * (0.075/100)
            portfolio = 0
            buy = graph.loc[row,"BUY"] = price
            position = True
            #print('buy bench',graph.loc[row,'benchmark'])
            TSL = sarUP
        
            graph.loc[row,'benchmark'] = price
            TSLL = price - (price*0.01)        
        
        if  high >= profit and position == True:
            print('buy',buy,'sell',price,'profit',profit,'stop_loss',stop_loss,'minutes: ',count)    
            count = 0
            if price<=stop_loss or price>=profit:
                cycle = False
            else:
                cycle = True
            
            if price >= buy :
                win = win+1
                print('win')
            else:
                print('loose')
                loose = loose + 1
            if price> price:
                price = TSL
            graph.loc[row,"SELL"] = price
            portfolio = shares*profit
            fees += portfolio * (0.075/100)
            position = False
            graph.loc[row,"portfolio"] = portfolio

    change = calc_change(portfolio,starting_portfolio)     
            #getPortfolio(starting_portfolio,portfolio)   
    winRate = (win*100)/(win+loose)
    looseRate = 100 - winRate
    print(f"""
            ==========================================
                            OUTCOME
            ==========================================
            # 
            # Wins: {win} {winRate}
            #
            # Loose: [{loose}] {looseRate}
            # 
            # Portfolio: {portfolio}
            # change:{change}
            # fees : {fees}
            __________________________________________
            """)    
    return graph

#getPortfolio(starting_portfolio,portfolio)

#with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#    print(graph[['open-time','ATR']])

# function creating consolei
def get_unix_ms_from_date(date):
        return int(calendar.timegm(date.timetuple()) * 1000 + date.microsecond/1000)

def get_trades(symbol, from_id):
        r = requests.get("https://api.binance.com/api/v3/aggTrades",
        params = {
            "symbol": symbol,
            "limit": 1000,
            "fromId": from_id
            })

        return r.json()
def getMoreData(symbol,starting_data,ending_date):
    symbol = symbol
    starting_date = datetime.strptime(starting_date, '%m/%d/%Y')
    ending_date = datetime.strptime(ending_date, '%m/%d/%Y') + timedelta(days=1) - timedelta(microseconds=1)
    new_ending_date = from_date + timedelta(seconds=60)
    r = requests.get('https://api.binance.com/api/v3/aggTrades',
    params = {
    "symbol" : symbol,
    "startTime": get_unix_ms_from_date(from_date),
    "endTime": get_unix_ms_from_date(new_ending_date)
    })
    response = r.json()
    if len(response) > 0:
        return response[0]['a']
    else:
        raise Exception('no trades found')

    
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
    interval = input("enter interval: ")

    #testing functions
    #pastDATA = get_pastData(symbol,interval)
    pastDATA = extended_pastData(symbol,interval,5000)
    graph = create_dataFrame(pastDATA)
    #graph = pd.read_excel('trix/09Sep2021_1151_df - Copy.xlsx', sheet_name='Sheet')
    ema26 = calc_ema(graph,26)
    ema12 = calc_ema(graph,12)
    macd = calc_macd(ema12,ema26)
    ema6 = calc_ema(graph,6)
    ema3 = calc_ema(graph,3)
    ema200 = calc_ema(graph,100)
    atr = calculate_atr(graph,14) 
    graph['ATR'] = atr
    
    #adding ema to dataframe
    graph['EMA26'] = ema26
    graph['EMA12'] = ema12
    graph['EMA200'] = ema200
    graph['EMA6'] = np.round(ema6, decimals = 3)
    graph['EMA3'] = np.round(ema3, decimals = 3)
    graph['MACD'] = macd
    signal = graph['MACD'].ewm(span=9,adjust = False, ignore_na=False).mean()
    graph['signal'] = signal
    rsi = ta.momentum.StochRSIIndicator(graph['close'])
    graph['rsi'] = rsi.stochrsi_k()
    graph['sarUP'] = pta.SAR(graph['high'],graph['low'], acceleration= 0.02,maximum=0.2)
    graph['stoch'] = ta.momentum.StochasticOscillator(graph['high'],graph['low'],graph['close']).stoch()
    
    for row in range(2,len(graph.index)-2):
        if is_support(graph,row):
            graph.loc[row,'support'] = True
        else:
            graph.loc[row,'support'] = False

        if is_resistance(graph,row):
            graph.loc[row,'resistance'] = True
        else:
            graph.loc[row,'resistance'] = False
    
    graph = buy_sell(graph,100)
    
    #ploting graph
    """
    plot1 =plt.figure(1)
    plt.plot(graph['open-time'],graph['close'],label = "Price",zorder=1)
    plt.plot(graph['open-time'],graph['EMA9'], label= "ema9",zorder=1)
    plt.plot(graph['open-time'],graph['EMA6'], label= "ema6", zorder=1)
    plt.plot(graph['open-time'],graph['EMA3'], label= "ema3",zorder=1)
    """
    plot2= plt.figure(2)
    plt.plot(graph['open-time'],graph['close'],label = "Price",zorder=1)
    
    plt.scatter(graph['open-time'],graph['BUY'],label="buy",color='green')
    plt.scatter(graph['open-time'],graph['SELL'],label="sell",color = 'red')  
    for i in graph.index:
        if graph.loc[i,'resistance']:
            pass
            #plt.scatter(graph.loc[i,'open-time'],graph.loc[i,'close'],marker ='v', color='r')
        if graph.loc[i,'support']:
            pass
            #plt.scatter(graph.loc[i,'open-time'],graph.loc[i,'close'],marker='^',color='green')
    plot3 = plt.figure(3)
    plt.plot(graph["open-time"], graph['portfolio'], marker = 'o',label = "Portfolio")



    plt.xlabel("time")
    plt.ylabel("price")

    plt.legend()
    plt.show()

#every time websocet recieves a msg this function is called
# and List is updated so graph can update 
def on_message(List,sale,starting_data,symbol,interval,ws,message):
     
    message2 = json.loads(message) 
    #if x and position true
    if starting_data['position'] == True:
        
        if starting_data['benchmark']>float(message2['k']['c']):
            print(starting_data['benchmark'],float(message2['k']['c']))
        else:
            benchmark = starting_data['benchmark'] = float(message2['k']['c'])
            TSL=starting_data['TSL'] = benchmark - starting_data['ATR']
            print('bencmark',benchmark,'TSL',TSL,'price',float(message2['k']['c']))
        

        sell_action,take_profit,stop_loss = sell(0,0,float(message2['k']['c']),starting_data,symbol,interval) #calls sell func if conditons are met
        
        if sell_action: #if sell returns true sale data list updated
            print('sell action iquals Truee')
            data = message2['k']
            NaN = np.nan
            time = datetime.datetime.utcfromtimestamp(message2['E']/1000)
            sale.append([time,float(data['c']),float(starting_data['portfolio']),take_profit,stop_loss])
        
                    
    if message2['k']['x']==True: #every time a candel closes main data list is updated
        data = message2['k']
        NaN = np.nan
        time = datetime.datetime.utcfromtimestamp(message2['E']/1000)    
        List.append([time,float(data['o']),float(data['h']),float(data['l']),float(data['c']),NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN])
        print('new candle')        
         
def on_close():
    print('FAGNER, CONNECTION HAS BEEN CLOSED!!!')
           
#initializes websocket args: symbol and List (List shared between process )           
def getCandels(symbol,interval,List,sale,starting_data):
    
    url = f'wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}'
    ws= websocket.WebSocketApp(url, on_message=on_message,on_close=on_close) # starts websockets
    ws.on_message = lambda *x: on_message(List,sale,starting_data,symbol,interval, *x) # passes arguments to func that is called every time we receive data from sockets
    ws.run_forever()


def buy(rsi,ema100,signal,lowest,macd,ema3,ema6,ema9,price,time,starting_data,atr,symbol,interval):
    
    if signal > macd:
        starting_data['CYCLE'] = True
    print('buy','signal',signal,'macd',macd,'rsi',rsi)    
    if signal<macd and starting_data['position'] == False and rsi>0.20 and rsi<0.80 and starting_data['CYCLE']==True:
           
        shares = starting_data['portfolio']/price
        shares = round(shares,starting_data['step_size'])
        #response =place_order(symbol,'BUY','MARKET',shares) #calls funct that places order   
        response= True

        #if  response['status'] == 'filed': #if order is placed properly     
        if response: 
            #updates starting data
            #actual_price=  sum(float(fill['price'])for fill in response['fills'])/len(response['fills'])
            #payed_price = sum(float(fill['price'])*float(fill['qty']) for fill in response['fills'])
            starting_data['benchmark'] = price #test
            payed_price = actual_price = price #test
            stop_loss=starting_data['stop_loss'] = price-atr # changed to hold price value NOT STOP LOSS
            starting_data['TSL'] = price - atr
            profit=starting_data['profit'] = actual_price + (actual_price * 0.0020)#test (atr*1.5)
            starting_data['starting_portfolio'] = starting_data['portfolio']
            #qty = starting_data['shares'] = float(response['executedQty'])
            qty = starting_data['shares'] = shares 
            starting_data['portfolio'] = 0
            starting_data['position'] = True
            starting_data['ATR'] = atr
            starting_data['buy'] = price #test
            

            print(f"""
            --------------------------------------------------------------------------------
                                            BUY
            --------------------------------------------------------------------------------
            | price_sent:   {price}
            | actual_price: {actual_price}
            | payed_price:  {payed_price}
            | qty:          {qty}
            | ATR:          {atr}
            ________________________________________________________________________________
            | profit:       {profit}
            | stop_loss:    {stop_loss}  
            ================================================================================
            """)
            playsound('cash.mp3')
            return True # returns that it was placed
                 
        else:
            
            print('order not filled')    
            return False  # returns that order wasnt placed

    return False    #if everything goes wrong, returs that order wasnt placed  

def sell(signal,macd,price, starting_data,symbol,interval):
    
    profit = starting_data['profit']
    position = starting_data['position'] 
    stop_loss = starting_data['stop_loss']
    shares = starting_data['shares']
    is_profit=0
    is_loss =0
    
    if price <= starting_data['TSL'] and position == True:
        starting_data['CYCLE']=False
    # checks that there is a position and conditions for sale a met
    #if signal > macd and position==True or price>= profit and position==True:
    #if price >= profit and position==True or price <= stop_loss  and position == True:
    
    #if price<=starting_data['TSL']: #test
    if price>=profit:
    #response = place_order(symbol,'SELL','MARKET',shares) # calls order func
        response = True # test delete
        if response: #if order is placed  starting data list is updated
            
            if price>= starting_data['buy']: #test should be sotp_loss
                is_profit=1
                is_loss=0
                starting_data['wins']+=1 
            else:
                is_profit=0
                is_loss=1
                starting_data['losses']+=1
            
            wins = starting_data['wins']
            losses = starting_data['losses']
            winsPercentage = (wins*100)/(wins+losses)
            lossesPercentage = (losses*100)/(wins+losses)
            #qty = float(response['executedQty'])
            qty = starting_data['shares'] #test delete
            #price = sum(float(fill['price']) for fill in response['fills'])/len(response['fills'])
            #portfolio = sum(float(fill['price'])*float(fill['qty']) for fill in response['fills'])
            portfolio = price * qty # test delete
            starting_data['portfolio']=portfolio
            starting_data['position'] = False # sets postion to no longer active

            res =client.account()
            USDT = 0

            for asset in res['balances']:
                if asset['asset'] =='USDT':
                    USDT=asset['free']
            print(portfolio,starting_data['starting_portfolio'])
            portfolio_change = calc_change(portfolio,starting_data['starting_portfolio'])
            
            print(f"""
            --------------------------------------------------------------------
            ##########################**SELL**##################################
            --------------------------------------------------------------------
            | Price:        ${price}
            | Qty:          {qty}
            | portfolio**:  ${portfolio}
            | Is profit? :  {is_profit}
            | wins = {wins} {winsPercentage}%
            | losses = {losses} {lossesPercentage}%
            | USDT = ${USDT}
            | Portifolio : {portfolio_change}%
            ====================================================================
            """)
            playsound('cash.mp3')
            return  True, is_profit, is_loss; # returns that order was completed 
    
    return False ,is_profit,is_loss;     # returns that order failed   

#Animate function is called by ploting function every second
def animate(self,List,sale,df,sale_df,starting_data,symbol,interval,df_csv_name):
    
    data =list(List) #turns proxy main list into local list
    sale_data = list(sale) #turns proxy main list into local list
    sale_df_size=len(sale_df.index) #gests sales  dataframe size 
    sale_data_size = len(sale_data) #get sale list size
    size = len(data) # gets main  data list size .. t
    df_size = len(df.index) # get main dataframe size

    if size> 0: # if main data size > 0

        if  df.loc[df_size-1,'open-time'] != data[size-1][0]: #checks if there is new row in data list/ checks for new candel
 #          print(len(data[size-1]))            
            
            df.loc[df_size]= data[size-1] # adds new row to main dataframe
            # Calculates new EMA
            ema200 = calc_ema(df,200)
            ema26 = calc_ema(df,26)
            ema12 = calc_ema(df,12)
            ema9 = calc_ema(df,9)
            ema6 = calc_ema(df,6)
            #ema3 = calc_ema(df,3)
            take_profit=0            
            stop_loss=0
            atr = calculate_atr(df,14) #Calculates new ATR
            
            df['ATR'] = atr
            df['EMA9'] = ema9
            df['EMA6'] = ema6
            df['EMA3'] = df['close'].pct_change()
            df['EMA12'] = ema12
            df['EMA26'] = ema26
            df['EMA200'] = ema200
            df.loc[df_size, 'MACD']= df.loc[df_size, 'EMA12']-df.loc[df_size, 'EMA26']
            df['signal'] = df['MACD'].ewm(span=9,adjust = False, ignore_na=False).mean()
            rsi = ta.momentum.StochRSIIndicator(df['close'])
            df['rsi'] = rsi.stochrsi_k()
            print(df['EMA3'].iloc[-1])
            if not starting_data['position'] and  pd.isna(df.loc[df_size,'SELL']): # if there is no active positon
                # runs buy func returns true or false
                if interval == '1m' and starting_data['skip']>0:
                    starting_data['skip']=starting_data['skip'] - 1
                    
                buy_action = buy(df['rsi'].iloc[-1],df['EMA200'].iloc[-1],df['signal'].iloc[-1],df.loc[df_size, 'low'],df.loc[df_size, 'MACD'],df.loc[df_size,'EMA3'],df.loc[df_size,'EMA6'],df.loc[df_size,'EMA9'],df.loc[df_size,'close'],df.loc[df_size,'open-time'],starting_data,df.loc[df_size,'ATR'],symbol,interval)
            
                if buy_action:  
                    df.loc[df_size,'BUY'] = df.loc[df_size,'close']#adds buy price to data frame
            
            if starting_data['position']: # if there is an open position
                sell_action,take_profit,stop_loss = sell(df['signal'].iloc[-1],df['MACD'].iloc[-1],df.loc[df_size,'close'],starting_data,symbol,interval) #calls sell func if conditons are met
                if sell_action: #if sell returns true sale data list updated
                    NaN = np.nan            
                    sale.append([df['open-time'].iloc[-1],df.loc[df_size,'close'],float(starting_data['portfolio']),take_profit,stop_loss])
                                 

            wb = openpyxl.load_workbook(df_csv_name)
            ws = wb.active
            startRow = ws.max_row +1
            newRow =df.iloc[-1].tolist()
            ws.append(newRow)
            wb.save(filename=df_csv_name)
            wb.close()
# if new sale row, row is added to sale df.. sale has its own df, so it can be ploted properly with price plot
    if sale_data_size>0 and sale_df_size ==0 or sale_data_size>0 and sale_df.loc[sale_df_size-1,'time'] < sale[sale_data_size-1][0]:     
        sale_df.loc[sale_df_size] = sale_data[sale_data_size-1] 
        wb = openpyxl.load_workbook(df_csv_name)
        ws = wb.get_sheet_by_name('portfolio')
        startRow = ws.max_row +1
        newRow = sale_data[sale_data_size-1]
        ws.append(newRow)
        wb.save(filename=df_csv_name)
        wb.close()        
        
        
    # data potting 
   
    plt.subplot(2,1,1) 
    plt.cla()
    plt.plot(df['open-time'],df['close'],label = "Price")
    plt.scatter(df['open-time'],df['BUY'],label = "Buy",color='green')
    plt.scatter(sale_df['time'],sale_df['price'],label='price', color='red')
    
    plt.subplot(2,1,2)
    plt.cla()
    plt.scatter(sale_df['time'],sale_df['portfolio'],label ='portfolio',color='black')
    plt.legend(loc='upper left')
    plt.tight_layout()


"""

fucion that plots the graph with previous data and initializes animate function.
function meant to be used with Multporcessing.

"""
def ploting(List,sale,starting_data,symbol, interval):
    
    data_set= get_pastData(symbol,interval) #gest past data so it can be ploted
    df = create_dataFrame(data_set) # creates data frame with past data
    sale_df = pd.DataFrame(columns = ["time","price",'portfolio','take-profit','stop-loss'])#creates data frame to host sales data
    ema200 = calc_ema(df,200)
    ema26 = calc_ema(df,26)
    ema12 = calc_ema(df,12)
    ema9 = calc_ema(df,9)
    ema6 = calc_ema(df,6)
    #ema3 = calc_ema(df,3)
    macd = calc_macd(ema12,ema26)
    
    df['EMA12'] = np.round(ema12, decimals = 3 )
    df['EMA26'] = np.round(ema26, decimals = 3)
    df['EMA200'] = ema200
    df['EMA9'] = np.round(ema9, decimals = 3)
    df['EMA6'] = np.round(ema6, decimals = 3)
    df['EMA3'] = df['close'].pct_change()  
    df['MACD'] = macd
    atr = calculate_atr(df,14)
    df['ATR'] = atr
    df['signal'] = df['MACD'].ewm(span=9,adjust = False, ignore_na=False).mean()
    rsi = ta.momentum.StochRSIIndicator(df['close'])
    df['rsi'] = rsi.stochrsi_k()

    now = datetime.datetime.now()
    current_time = now.strftime("%d%b%Y_%H%M")
    
    df_csv_name = f'{current_time}_df.xlsx'
    sale_csv_name = f'{current_time}_sale.csv'
    directory = os.getcwd()
    directory = f'{directory}/trix/{df_csv_name}'
    wb = openpyxl.Workbook()
    ws = wb.active
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r) 
    wb.create_sheet('portfolio')
    ws2 = wb.get_sheet_by_name('portfolio')

    for r in dataframe_to_rows(sale_df, index=False, header = True):
        ws2.append(r)
    wb.save(directory)
    ani = FuncAnimation(plt.gcf(), animate,fargs=(List,sale,df,sale_df,starting_data,symbol,interval,directory), interval=1000)# animates plot everysecond by caling animate func
    plt.show()

def run_sockets(List,sale,starting_data,symbol,interval): #process
    getCandels(symbol,interval,List,sale,starting_data)
   
   
def foo():
    print("TESTINGG")

def invalid_input():
    print("invalid command :( ")

# main
def main():
    #actions connected to function
    cmd_actions = {'foo':foo,'simulation':simulation,"tradingTest":trading_test}
    
    cmd_queue =  queue.Queue()

    dj = threading.Thread(target = console, args = {cmd_queue})
    dj.start()

    while 1:
        ccmd = cmd_queue.get()
        if cmd == 'quit':
            break
        action = cmd_actions.get(cmd, invalid_input)
        action()

def trade():
    
    symbol = input("enter symbol: ")
    interval = input("enter interval to trade in: ")
    manager = mp.Manager()
    symbol_info = r.get(f'https://api.binance.com/api/v3/exchangeInfo?symbol={symbol.upper()}').json()
    List = manager.list() #list to be shared between processes
    sale = manager.list()#list used to store a 
    starting_data = manager.dict() #dict that holds starting data 
    portfolio =input('enter value to be traded: ')
    for filt in symbol_info['symbols'][0]['filters']:
        if filt['filterType'] == 'LOT_SIZE':
            step_size = filt['stepSize'].find('1') - 2
            if step_size<0:
                step_size=0
            starting_data['step_size'] = step_size
            print(f'step_size: {step_size}')
            break
   
    
    # populating dict 
    starting_data['skip'] = 0
    starting_data['position'] = False
    starting_data['stop_loss'] = 0
    starting_data['profit'] =0
    starting_data['portfolio']= float(portfolio)
    starting_data['starting_portfolio'] = float(portfolio)
    starting_data['shares'] = 0
    starting_data['wins']=0
    starting_data['losses'] = 0
    starting_data['USDT'] = 0
    starting_data['CYCLE'] = True # controls if buying is allowed
    starting_data['benchmark'] = 0
    starting_data['ATR'] = 0
    starting_data['buy'] = 0

    res =client.account()
    for asset in res['balances']:
        if asset['asset'] =='USDT':
            starting_data['USDT'] = asset['free']
            print(asset['free'])
    
    freeze_support() # seems to be mandatory
    p1=mp.Process(target=run_sockets, args=(List,sale,starting_data,symbol,interval)) #creates process 1
    p2=mp.Process(target=ploting, args=(List,sale,starting_data,symbol,interval))   # creates process 2
    # starts process 
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
def menu(args):
    if args[1] == '-h':
        print()
        print("""
               1- cancel all open orders for specific symbol:
                  python3 cryptoTrading.py cancel_all <SYMBOL>
               
               2- get account details:
                  python3 cryptoTrading.py account                  
                
               3- sells everthing:
                  python3 cryptoTrading.py sell_all <SYMBOL>  
                  """)
    if args[1] == 'cancel_all':
        if len(args) !=3:
            print('python3 cryptoTrading.py cancel_all <SYMBOL>')
        else:
            cancel_all_open_orders(args[2].upper())
    if args[1]=='account':
        if len(args) !=2:
            print('python3 cryptoTrading.py account')
            
        else:
            res =client.account()
            for asset in res['balances']:
                if asset['asset'] =='USDT':
                    print(asset['free'])

    if args[1]=='trade':
        if len(args) !=2:
            print('python3 cryptoTrading.py simulate')
        else:
            trade()
    if args[1] == 'simulate':
        if len(args) !=2:
            print('Wrong!')
        else:
            simulation()
    if args[1]=='sell':
        if len(args)!=2:
            print('python3 cryptoTrading.py sell')
        else:
            print(client.account())
            symbol = input('enter symbol: ')
            qty = input('enter qty: ')
            response = place_order(symbol,'SELL','MARKET',qty)
            print(response)
if __name__ == '__main__':
    if len(args)>1:        
        menu(args)
        

