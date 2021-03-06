"""
https://api.binance.com/api/v1/exchangeInfo    
https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h
"""
import requests as r 
import pandas as pd
import numpy as np
import websocket
import json
from playsound import playsound
# Global Variables
symbols_names = []
stocks = {}
counter=0
hour_counter = 0
symbols_names_copy=[]
not_working= ['DAIUSDT','USDPUSDT']

def calc_change(new,old):
    change = ((new-old)/old)*100
    return change

def on_close(ws, message):
    print('conection closed!!')

def calc_ema(dataset,n):
    ema = dataset.ewm(span=n,adjust=False, ignore_na=False).mean()
    return ema


def find(lst, key, value): # Finds index by value 
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1

def calc_macd(ema12,ema26): 
    macd = []
    for i in range(len(ema12)):
        hold = ema12[i] - ema26[i]
        macd.append(hold)
    return macd


def on_message(ws, message):
    global symbols_names_copy 
    message = json.loads(message)
    symbol = message['s']
    data = message['k']
    if symbol=='DAIUSDT':
        print('dai')
    if data['x'] and symbol.lower() in symbols_names_copy: #candle is closed
        global counter
        global hour_counter
        
        symbols_names_copy.remove(symbol.lower())
        counter = counter + 1 # add one to counter *used to check if all symbols have closed the minute candle
        
        # every minute data is added to DF
        df = stocks[symbol] #retrives df for that symbol
        size = len(df.index)
        df.loc[size] = ['na',float(data['c']),'na','NA','NA','na','na','na','na','na','na','signal','ema12','ema26','macd','change'] # inserts new row
          
       # Calculates emas and Macds
        
        df['ema12M']= calc_ema(df['priceMinute'],12)
        df['ema26M']= calc_ema(df['priceMinute'],26)
        
        macdM=df.loc[size,'macdM'] =df.loc[size,'ema12M'] - df.loc[size,'ema26M']
        signalM = df['signalM'].iloc[-1] = calc_ema(df['macdM'],9) # ema from macds
        priceChange = df.loc[size,'priceChangeM'] = ((df.loc[size,'priceMinute']-df.loc[size-1, 'priceMinute' ])/ df.loc[size-1,'priceMinute'])*100
        macdChangeM = df.loc[size,'macdChangeM'] = ((df.loc[size,'macdM'] - df.loc[size-1, 'macdM']) / df.loc[size-1,'macdM']) * 100 #macd change
        
        if  hour_counter == 60: # add hour data and return infos
            
            df.loc[size,'priceHour'] = float(data['c']) # add hourly price
            
            # new DF containing hourly data. 
            dfH = df[df['priceHour'] != 'na']
            # calculate Hourly ema
            dfH['ema12H'] = calc_ema(dfH['priceHour'],12)
            dfH['ema26H'] = calc_ema(dfH['priceHour'],26)

            # Calculating hourly macd and Signal
            df['macdH'].iloc[-1] =  dfH['macdH'].iloc[-1] = dfH['ema12H'].iloc[-1] - dfH['ema26H'].iloc[-1] 
            df['signalH']=dfH['signalH'] = calc_ema(dfH['macdH'],9) # ema from hourly macds
            df.loc[size,'priceChangeH'] = calc_change(dfH['priceHour'].iloc[-1],dfH['priceHour'].iloc[-2])
            df.loc[size,'macdChangeH'] = calc_change(dfH['macdH'].iloc[-1],dfH['macdH'].iloc[-2])#macd change
            
            print('ONE HOUR HAS PASSED',counter,'/',len(symbols_names))
            
        if counter == len(symbols_names) and hour_counter == 60:           
            
            rankedStoks ={k:stocks[k] for k in sorted(stocks, key=lambda x: stocks[x].priceChangeH.iloc[-1], reverse=True)} #sorting the DF
                
            
            i=1 # i counts the ranks 
            print(1)
            for key,values in rankedStoks.items(): 
            
                HourPriceChange = values.priceChangeH.iloc[-1]
                macdH = values.macdH.iloc[-1]
                signalH = values.signalH.iloc[-1]
                macdChangeH = values.macdChangeH.iloc[-1] 
                
                macdM =  values.macdM.iloc[-1]
                signalM= values.macdM.iloc[-1]
                
                if signalH >= macdH:
                    signalH = 'True'
                else:
                    signalH = 'False'

                if signalM >=  macdM:
                    signalM ='True'
                else:
                    signalM = 'False'
                
                print(f'{i}# symbol: {key} macdChangeH: {macdChangeH} priceChange: {HourPriceChange}% Hourly_signal: {signalH} Minute_signal: {signalM}')
                
                i=i+1
            
            print('---------------------------------------------------')    
            hour_counter = 0
            playsound('bell.wav')
        
        if counter == len(symbols_names):
            symbols_names_copy = symbols_names.copy()
            counter = 0     
            hour_counter = hour_counter + 1
            print(f" hour counter: {hour_counter}")

def change():
    global symbols_names_copy
    response = r.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h').json()

    newlist = sorted(response, key=lambda k: k['price_change_percentage_1h_in_currency'] if k['price_change_percentage_1h_in_currency'] else 0)
    rank = 0

      # Selecting the top 20    
    for i in range(99,00,-1):
        new_symbol = newlist[i]['symbol'].upper()
        oneH=round(newlist[i]['price_change_percentage_1h_in_currency'],3)
        two4H =round(newlist[i]['price_change_percentage_24h'],3)
        price = newlist[i]['current_price']
        new_symbol = new_symbol+'USDT'
        response  = r.get(f'https://api.binance.com/api/v3/exchangeInfo?symbol={new_symbol}')
     
        if response.status_code==200: #if in Binance
            rank += 1
            if new_symbol  in not_working:
                pass
            else:
                symbols_names.append(new_symbol.lower())
            dataMinute = r.get(f"https://api.binance.com/api/v3/klines?symbol={new_symbol}&interval=1m&limit=150").json() # getting historical data 
            dataHour = r.get(f"https://api.binance.com/api/v3/klines?symbol={new_symbol}&interval=1h&limit=150").json()   # getting historical data       
            
            my_col = ['priceHour','priceMinute','priceChangeM','priceChangeH','signalH','ema12H','ema26H','ema100M','macdH','signalM','ema12M','ema26M','ema100H','macdM','macdChangeM','macdChangeH']

            df = pd.DataFrame(columns= my_col) # creating data
            for candleHour, candleMinute in zip(dataHour,dataMinute): # populates data 
                df = df.append(
                        pd.Series([
                            float(candleHour[4]),
                            float(candleMinute[4]),
                            'N/A',
                            'N/A',
                            'na',
                            'na',
                            'na',
                            'na',
                            'na',
                            'na',
                            0,
                            0,
                            0,
                            0,0,0
                            ],index= my_col),

                            ignore_index = True
                        )
            
            # calculates ema, macd and signal HOUR 
            df['ema12H']= calc_ema(df['priceHour'],12)
            df['ema26H']= calc_ema(df['priceHour'],26)
            df['macdH'] = calc_macd(df['ema12H'],df['ema26H'])
            df['ema100H'] = calc_ema(df['priceHour'],100)
            macdH = df['macdH'].loc[len(df)-1] = df['ema12H'].loc[len(df)-1] -  df['ema26H'].loc[len(df)-1]
            df['signalH']= calc_ema(df['macdH'],9)

            # calculates ema, macd and signal Minute
            df['ema12M']= calc_ema(df['priceMinute'],12)
            df['ema26M']= calc_ema(df['priceMinute'],26)
            df['macdM'] = calc_macd(df['ema12M'],df['ema26M'])
            df['ema100M'] = calc_ema(df['priceMinute'],100)
            macdM=df.loc[len(df)-1,'macdM'] =df.loc[len(df)-1,'ema12M'] -  df.loc[len(df)-1,'ema26M']
            df['signalM']= calc_ema(df['macdM'],9)

            signalH ='False'    
            signalM = 'False'
            
            if df['signalH'].iloc[-1]<df['macdH'].iloc[-1]:
                signalH = 'True'
            else:
                signal = 'False'
           

            if df['signalM'].iloc[-1] < df['macdM'].iloc[-1]:
                signalM= 'True'
            else:
                signal = 'False '
            if new_symbol  in not_working:            
                pass
            else:
                stocks[new_symbol] = df
            ema100H = df.ema100H.iloc[-1]
            ema100M = df.ema100M.iloc[-1]
            print( f'{rank}# {new_symbol}: price: {price} ema100M:{ema100M} ema100H:{ema100H} 1h: {oneH}% 24h: {two4H}% SIGNAL_H:{signalH},SIGNAL_M:{signalM}')

    
    url = f'wss://stream.binance.com:9443/ws/'
    url = url + '@kline_1m/'.join(symbols_names)+'@kline_1m'
    print(url)
    symbols_names_copy = symbols_names.copy()
    ws= websocket.WebSocketApp(url, on_message=on_message,on_close=on_close)
    ws.run_forever()
change()
        
        
