"""
https://api.binance.com/api/v1/exchangeInfo    
https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h
"""
import requests as r 

def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


response = r.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1h').json()


newlist = sorted(response, key=lambda k: k['price_change_percentage_1h_in_currency'])

for coin in newlist:
    symbol =coin['symbol']
    oneH=coin['price_change_percentage_1h_in_currency']
    two4H=coin['price_change_percentage_24h']
    price = coin['current_price']
    
    print( f'{symbol}: price: {price} 1h: {oneH}% , 24h: {two4H} ')

current_coin_index = find(newlist,'symbol','btc')
if current_coin_index < 99:
    print(newlist[99]['price_change_percentage_1h_in_currency'],newlist[current_coin_index]['price_change_percentage_1h_in_currency'])
print(current_coin_index)
