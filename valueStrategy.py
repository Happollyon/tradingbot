"""Value investing" means investing in the stocks that are cheapest relative to common measures of business value (like earnings or assets).
"""
import pandas as pd 
import requests as r 
import numpy as np 
import xlsxwriter
from scipy import stats
import math
from secret import IEX_TOKEN


stocks = pd.read_csv('sp_500_stocks.csv')

# this function breaks the 500 stoks into chunks of n
def chunck(lst, n):
    for i in range(0, len(lst),n):
        yield lst[i:i + n]



# chunks of 100
symbol_groups = list(chunck(stocks['Ticker'],100))
symbol_string = []


# we create a string with the 100 symbols separeted by , 
for i in range(0, len(symbol_groups)):
    symbol_string.append(','.join(symbol_groups[i]))
  

my_columns = ['Ticker','Price','Price-to-earnings Ratio', 'Number of shares to buy']
final_dataframe = pd.DataFrame(columns = my_columns)

for string in symbol_string:
    url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={string}&token={IEX_TOKEN}'
    data = r.get(url).json()

    for symbol in string.split(','):
        final_dataframe = final_dataframe.append(
                    pd.Series([
                        symbol,
                        data[symbol]['quote']['latestPrice'],
                        data[symbol]['quote']['peRatio'],
                        'N/A'

                        ],
                            index = my_columns
                        ),
                    ignore_index = True
                )

print(final_dataframe)
    
