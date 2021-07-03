
#numpy runs in c++ which is really fast. 
import numpy as np
# pandas makes it easy to work with tabular data. 
import pandas as pd
import requests as r
import math

stocks = pd.read_csv('sp_500_stocks.csv')
from secret import IEX_TOKEN

# This functions splits the list into chuncks of 100
def chunks(lst, n) :
        for i in range(0, len(lst),n):
            yield lst[i:i+n]


symbol_groups = list(chunks(stocks['Ticker'],100))
#now we transform all the stock in the lists into a string so we can pass in the url

symbol_strings = []
for i in range(0,len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
    

# Adding our scks price to a pandas DataFrame
my_columns = ['Ticker', 'Stock Price','Market Cap', 'Number of shares to buy']
final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
    batch_api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string},fb&types=quote&token={IEX_TOKEN}'
    #api_url = f'https://sandbox.iexapis.com/stable/stock/{stock}/quote/?token={IEX_TOKEN}'  
    data = r.get(batch_api_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
        pd.Series(
            [
             symbol,
             data[symbol]['quote']['latestPrice'],
             data[symbol]['quote']['marketCap'],
             'N/A'
            ],
            index = my_columns),
            ignore_index=True
            
        
        )
print(final_dataframe)

   

