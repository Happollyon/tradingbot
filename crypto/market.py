"""

https://api.binance.com/api/v1/exchangeInfo    
https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h
"""
import requests as r 
import pandas as pd
import numpy as np

def calc_ema(dataset,n):
    ema = dataset.ewm(span=n).mean()
    return ema

def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


response = r.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h').json()


newlist = sorted(response, key=lambda k: k['price_change_percentage_1h_in_currency'])

"""for coin in newlist:
    symbol =coin['symbol']
    oneH=coin['price_change_percentage_1h_in_currency']
    two4H=coin['price_change_percentage_24h']
    price = coin['current_price']    
   
    if oneH > two4H:
        difference = 'hour > 24'  
    else:
        difference = 'hour < 24'
    print( f'{symbol}: price: {price} 1h: {oneH}% , 24h: {two4H} {difference}')
"""
current_coin_index = find(newlist,'symbol','btc')

   
for i in range(99,89,-1):
    new_symbol = newlist[i]['symbol'].upper()
    oneH=newlist[i]['price_change_percentage_1h_in_currency']
    two4H =newlist[i]['price_change_percentage_24h']
    price = newlist[i]['current_price']
    new_symbol = new_symbol+'USDT'
    response  = r.get(f'https://api.binance.com/api/v3/exchangeInfo?symbol={new_symbol}')
    if response.status_code==200:
        dataMinute = r.get(f"https://api.binance.com/api/v3/klines?symbol={new_symbol}&interval=1m&limit=27").json()          
        dataHour = r.get(f"https://api.binance.com/api/v3/klines?symbol={new_symbol}&interval=1h&limit=27").json()          
        my_col = ['priceHour','priceMinute','ema9H','ema12H','ema26H','macdH','ema9M','ema12M','ema26M','macdM']

        df = pd.DataFrame(columns= my_col)
        for candleHour, candleMinute in zip(dataHour,dataMinute):
            df = df.append(
                    pd.Series([
                        float(candleHour[4]),
                        float(candleMinute[4]),
                        'N/A',
                        'na',
                        'na',
                        'na',
                        'na',
                        'na',
                        'na',
                        'na'
                        ],index= my_col),

                        ignore_index = True
                    )


        df['ema9H']= calc_ema(df['priceHour'],9)
        df['ema12H']= calc_ema(df['priceHour'],12)
        df['ema26H']= calc_ema(df['priceHour'],26)
        macdH=df['macdH'].loc[len(df)-1] =df['ema12H'].loc[len(df)-1] -  df['ema26H'].loc[len(df)-1]
        df['ema9M']= calc_ema(df['priceMinute'],9)
        df['ema12M']= calc_ema(df['priceMinute'],12)
        df['ema26M']= calc_ema(df['priceMinute'],26)
        macdM=df['macdM'].loc[len(df)-1] =df['ema12M'].loc[len(df)-1] -  df['ema26M'].loc[len(df)-1]
        print( f'{new_symbol}: price: {price} 1h: {oneH}% , 24h: {two4H} , MACDH: {macdH}, MACDM: {macdM}')


