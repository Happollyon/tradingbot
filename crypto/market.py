"""

https://api.binance.com/api/v1/exchangeInfo    
https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h
"""
import requests as r 
import pandas as pd
import numpy as np
import websocket
import json
symbols_names = []
stocks = {}


def on_message(ws, message):
    message = json.loads(message)
    symbol = message['s']
    data = message['k']
    
    if data['x']: #candle is closed
         
        
        df = stocks[symbol] #retrives df for that symbol
        size = len(df)
        df.loc[size] = ['na',float(data['c']),'na','na','na','na','na','ema9','ema12','ema26','macd','change'] # inserts new row
        
        # Calculates emas and Macds
        df['ema12M']= calc_ema(df['priceMinute'],12)
        df['ema26M']= calc_ema(df['priceMinute'],26)
        macdM=df.loc[size,'macdM'] =df.loc[size,'ema12M'] - df.loc[size,'ema26M']
        priceChange = df.loc[size,'priceChange'] = ((df.loc[size,'priceMinute']-df.loc[size-1, 'priceMinute' ])/ df.loc[size-1,'priceMinute'])*100
        macdChange=df.loc[size,'macdChange'] = ((df.loc[size,'macdM'] - df.loc[size-1, 'macdM']) / df.loc[size-1,'macdM']) * 100 #macd change
        print('symbol: ',symbol,'macd-1',df.loc[size-1,'macdM'],'macd',df.loc[size,'macdM'], 'macdChange',macdChange,'%', 'price_change: ',priceChange,'%')


def on_close(ws, message):
    print('conection closed!!')
def calc_ema(dataset,n):
    ema = dataset.ewm(span=n,adjust=False, ignore_na=False).mean()
    return ema

def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1

def change():
    response = r.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h').json()

    newlist = sorted(response, key=lambda k: k['price_change_percentage_1h_in_currency'] if k['price_change_percentage_1h_in_currency'] else 0)

      # Selecting the top 20    
    for i in range(99,95,-1):
        new_symbol = newlist[i]['symbol'].upper()
        oneH=newlist[i]['price_change_percentage_1h_in_currency']
        two4H =newlist[i]['price_change_percentage_24h']
        price = newlist[i]['current_price']
        new_symbol = new_symbol+'USDT'
        response  = r.get(f'https://api.binance.com/api/v3/exchangeInfo?symbol={new_symbol}')
     
        if response.status_code==200: #if in Binance
            symbols_names.append(new_symbol.lower())
            dataMinute = r.get(f"https://api.binance.com/api/v3/klines?symbol={new_symbol}&interval=1m&limit=27").json() # getting historical data 
            dataHour = r.get(f"https://api.binance.com/api/v3/klines?symbol={new_symbol}&interval=1h&limit=27").json()   # getting historical data       
            
            my_col = ['priceHour','priceMinute','priceChange','ema9H','ema12H','ema26H','macdH','ema9M','ema12M','ema26M','macdM','macdChange']

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
                            0,
                            0,
                            0,
                            0
                            ],index= my_col),

                            ignore_index = True
                        )

            # calculates ema and mads HOUR and Min
            df['ema9H']= calc_ema(df['priceHour'],9)
            df['ema12H']= calc_ema(df['priceHour'],12)
            df['ema26H']= calc_ema(df['priceHour'],26)
            macdH=df['macdH'].loc[len(df)-1] =df['ema12H'].loc[len(df)-1] -  df['ema26H'].loc[len(df)-1]
            df['ema9M']= calc_ema(df['priceMinute'],9)
            df['ema12M']= calc_ema(df['priceMinute'],12)
            df['ema26M']= calc_ema(df['priceMinute'],26)
            macdM=df.loc[len(df)-1,'macdM'] =df.loc[len(df)-1,'ema12M'] -  df.loc[len(df)-1,'ema26M']
            
            stocks[new_symbol] = df
            print( f'{new_symbol}: price: {price} 1h: {oneH}% , 24h: {two4H} , MACDH: {macdH}, MACDM: {macdM}')

    
    url = f'wss://stream.binance.com:9443/ws/'
    url = url + '@kline_1m/'.join(symbols_names)+'@kline_1m'
    print(url)
    ws= websocket.WebSocketApp(url, on_message=on_message,on_close=on_close)
    ws.run_forever()
change()
        
        
