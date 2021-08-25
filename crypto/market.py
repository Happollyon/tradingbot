"""
https://api.binance.com/api/v1/exchangeInfo    
https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h
"""
import requests as r 

response = r.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h').json()

newlist = sorted(response, key=lambda k: k['price_change_percentage_1h_in_currency'])

for coin in newlist:
    symbol =coin['symbol']
    oneH=coin['price_change_percentage_1h_in_currency']
    two4H=coin['price_change_percentage_24h']
    print( f'{symbol}: 1h: {oneH}% , 12h: {two4H} ')
