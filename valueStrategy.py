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

# sorting the 10 best stocks

final_dataframe.sort_values('Price-to-earnings Ratio', inplace = True)
# selects only the stocks with ratio greater than 0
final_dataframe = final_dataframe[final_dataframe['Price-to-earnings Ratio'] > 0]
#saves 10 top ratio
final_dataframe = final_dataframe[:10]
final_dataframe.reset_index(inplace = True)
final_dataframe.drop('index', axis=1,inplace =True)
# calculating the number of shares to buy
def portfolio_input():
    global portfolio
    portfolio = float(input('enter the size of your portfolio: '))

portfolio_input()
position_size = portfolio/10

for i in final_dataframe.index:
    final_dataframe.loc[i,'Number of shares to buy'] =  final_dataframe.loc[i,'Price'] / position_size
print(final_dataframe)    
