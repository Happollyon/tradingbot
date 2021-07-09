"""
quantantive momentum strategy means investing in stocks that have increased in price the most. With this bot we are going to select 10 oof the stocks that have increased the most and we will calculate recomended trades for an equal weight portfolio. 
"""
import pandas as pd
import math
import requests as r
import numpy as np
from secret import IEX_TOKEN
import xlsxwriter
from scipy import stats
from statistics import mean 

stock = pd.read_csv('sp_500_stocks.csv')

# breaks the 505 list of stocks into chunks of n number
def chunks(lst,n):
    for i in range(0, len(lst),n):
        yield lst[i:i+n]

symbol_groups = list(chunks(stock['Ticker'],100))
symbol_strings = []


def portfolio_input():
    global portfolio_size
    portfolio_size = input('enter portfolio size: ')
    try:
        float(portfolio_size)
    except ValueError:
        print('enter a  number')
portfolio_input()




# turns the group of 100 stocks into string spareted by comma
for i in range(0,len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
   

my_columns = [
        
        'Ticker',
        'Price',
        'Number of shares to buy',
        'One year return',
        'One year %',
        'Six months return',
        'Six months %',
        'Three months return',
        'Three months %',
        'One month return',
        'One month %',
        'HQM Score'
        
        ]

time_period = ['One year','Six months','Three months', 'One month']

# creates dataframe using pandas
final_dataframe = pd.DataFrame(columns = my_columns)

#makes the bach call and populates the dataframe 
for symbol_string in symbol_strings[:3]:
    batch_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote,stats&symbols={symbol_string}&token={IEX_TOKEN}'
    
    data = r.get(batch_url)

    data=data.json()
 
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
                    pd.Series(
                        [
                            symbol,
                            data[symbol]['quote']['latestPrice'],
                            'NaN',
                            data[symbol]['stats']['year1ChangePercent'],
                            'NaN',
                            data[symbol]['stats']['month6ChangePercent'],
                            'NaN',
                             data[symbol]['stats']['month3ChangePercent'],
                             'NaN',
                             data[symbol]['stats']['month1ChangePercent'],
                             'NaN',
                            'NaN'                            
                        ],
                            index = my_columns
                        ), ignore_index = True
    
                )
       
        
# Calculatin the High quantitive momentum score 
for row in final_dataframe.index:
    for period in time_period:
        
        # some of the 
        if final_dataframe.loc[row, f'{period} %'] == None:
            print('%')
            final_dataframe.loc[row, f'{period} %'] = 0.0
        if final_dataframe.loc[row, f'{period} return']== None:
            print('r')
            final_dataframe.loc[row, f'{period} return'] = 0.0


for row in final_dataframe.index:
    for period in time_period:

        final_dataframe.loc[row,f'{period} %'] =  stats.percentileofscore(final_dataframe[f'{period} return'],final_dataframe.loc[row,f'{period} return'])
        

# the HQM  score is the mean of the 4 momentum percentile scores 
for row in final_dataframe.index:
    momentum_percentile = []
    for period in time_period:
        momentum_percentile.append(final_dataframe.loc[row,f'{period} %'])
    final_dataframe.loc[row,'HQM Score'] = mean(momentum_percentile)
    

# inplace = true modifies the data inside the dataframe so it stays sorted       
final_dataframe.sort_values(by = 'HQM Score', ascending = False)
final_dataframe = final_dataframe[:10]
final_dataframe.reset_index(drop = True,inplace = True)



#calculating the number of shares to buy
position_size = float(portfolio_size) / 10


for i in range(0, len(final_dataframe)):
    final_dataframe.loc[i,'Number of shares to buy'] = position_size/final_dataframe.loc[i,'Price']
    
# Formating the excel output
writer = pd.ExcelWriter('momentum_strategy.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(writer,sheet_name = 'Momentum Strategy', index = False)


my_columns = {
        
        'A':['Ticker'],
        'B':['Price'],
        'C':['Number of shares to buy'],
        'D':['One year return'],
        'E':['One year %'],
        'F':['Six months return'],
        'G':['Six months %'],
        'H':['Three months return'],
        'I':['Three months %'],
        'J':['One month return'],
        'L':['One month %'],
        'M':['HQM Score']
        

        }
for column in my_columns.keys():
    writer.sheets['Momentum Strategy'].set_column('A:A',32)

writer.save()    

