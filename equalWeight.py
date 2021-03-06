"""
    Fagner Nunes 05/07/2021

    This strategy spread all you funds among the available symbles. 
    This implementation of this stratagy is only for educational purpose, as it is likely to result in losse of money. 
    this bot doesnt place any order, as each broker has its own api and etc, but it will save the order in a excel file simulating a trading.
"""


#numpy runs in c++ which is really fast. 
import numpy as np
# pandas makes it easy to work with tabular data. 
import pandas as pd
import requests as r
import math

stocks = pd.read_csv('sp_500_stocks.csv')
from secret import IEX_TOKEN
import xlsxwriter
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
# calculating the number of shares to buy
portifolio_size = input("enter the size of your portifolio: ")
try:
    val = float(portifolio_size)
    print(val)
except:
    print("please enter a proprer value")
    portifolio_size = input("enter the size of your portifolio: ")
    val = float(portifolio_size)
position_size = val/ len(final_dataframe.index)

# calculate how many shares of the stock to buy
for i in range(0, len(final_dataframe.index)):
    # some brokers dont sell fractional shares, you can use math.floor to round down to nearst int
    final_dataframe.loc[i, 'Number of shares to buy'] = position_size/final_dataframe.loc[i,'Stock Price']

print(final_dataframe)

# now we save the order in a excel file. If you want you can modify this code to place the order in your behalf, to do that you need to read through your brokers api. 

# initilizing the excel writer -> in this case we are using pandas bcz pandas already uses tabulated data format
writer =pd.ExcelWriter('recomended_trades.xlsx', engine ='xlsxwriter' )
final_dataframe.to_excel(writer,'recomended_trades', index = False)

# creating xls format
background_color = '#0a0a23'
font_color = 'ffffff'

string_format = writer.book.add_format({
    'font_color': font_color,
    'bg_color': background_color,
    'border':1
    
    })
dollar_format = writer.book.add_format({
        'font_color': font_color,
        'bg_color': background_color,
        'border':1,
        'num_format': '$0.00'

                    })
integer_format = writer.book.add_format({
        'font_color': font_color,
        'bg_color': background_color,
        'border':1,
        'num_format': 0

                    })
writer.sheets['recomended_trades'].set_column('A:A',18,string_format)
writer.sheets['recomended_trades'].set_column('B:B',18,string_format)
writer.sheets['recomended_trades'].set_column('C:C',18,string_format)
writer.sheets['recomended_trades'].set_column('D:D',18,string_format)

writer.save()
