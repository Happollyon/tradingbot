
#numpy runs in c++ which is really fast. 
import numpy as np
# pandas makes it easy to work with tabular data. 
import pandas as pd
import requests as r
import math

stocks = pd.read_csv('sp_500_stocks.csv',nrows=10)
from secret import IEX_TOKEN


# Adding our scks price to a pandas DataFrame
my_columns = ['Ticker', 'Stock Price','Market Cap', 'Number of shares to buy']
final_dataframe = pd.DataFrame(columns = my_columns)

for stock in stocks['Ticker']:
    api_url = f'https://sandbox.iexapis.com/stable/stock/{stock}/quote/?token={IEX_TOKEN}'  
    data = r.get(api_url).json()
    final_dataframe = final_dataframe.append(
        pd.Series(
            [
             stock,
             data['latestPrice'],
             data['marketCap'],
             'N/A'
            ],
            index = my_columns),
            ignore_index=True
            
        
        )
print(final_dataframe)

   

