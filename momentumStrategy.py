"""
quantantive momentum strategy means investing in stocks that have increased in price the most. With this bot we are going to select 10 oof the stocks that have increased the most and we will calculate recomended trades for an equal weight portfolio. 
"""
import pandas as pd
import math
import requests as r
import numpy as np
from secret import IEX_TOKEN
import xlsxwriter



stock = pd.read_csv('sp_500_stocks.csv')

# breaks the 505 list of stocks into chunks of n number
def chunks(lst,n):
    for i in range(0, len(lst),n):
        yield lst[i:i+n]

symbol_groups = list(chunks(stock['Ticker'],100))
symbol_strings = []
# turns the group of 100 stocks into string spareted by comma
for i in range(0,len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
   

my_columns = ['Ticker', 'Price','One year return', 'Number of shares to buy']

# creates dataframe using pandas
final_dataframe = pd.DataFrame(columns = my_columns)
for symbol_string in symbol_strings[:3]:
    batch_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote,stats&symbols={symbol_string}&token={IEX_TOKEN}'
    #url = f'https://sandbox.iexapis.com/stable/stock/stats/stats?token={IEX_TOKEN}'
    
    data = r.get(batch_url)
    
    data=data.json()

    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
                    pd.Series(
                        [
                            symbol,
                            data[symbol]['quote']['latestPrice'],
                            data[symbol]['stats']['year1ChangePercent'],
                            'N/A'
                        ],
                            index = my_columns
                        ), ignore_index = True
    
                )
# inplace = true midifies the data inside the dataframe so it stays sorted       
final_dataframe.sort_values('One year return',ascending = False, inplace = True)
final_dataframe = final_dataframe[:10]
final_dataframe.reset_index(inplace = True)


#calculating the number of shares to buy
def portfolio_input():
    global portfolio_size
    portfolio_size = input('enter portfolio size: ')
    try:
        float(portfolio_size)
    except ValueError:
        print('enter a  number')
portfolio_input()

position_size = float(portfolio_size) / 10

for i in range(0, len(final_dataframe)):
    final_dataframe.loc[i,'Number of shares to buy'] = 0
