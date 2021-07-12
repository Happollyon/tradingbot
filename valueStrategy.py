"""Value investing" means investing in the stocks that are cheapest relative to common measures of business value (like earnings or assets).
"""
import pandas as pd 
import requests as r 
import numpy as np 
import xlsxwriter
from scipy import stats
import math
from secret import IEX_TOKEN
from statistics import mean


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
  

my_columns = [
        'Ticker',
        'Price',
        'Number of shares to buy',
        'Price-to-Earnings Ratio',
        'PE %',
        'Price-to-Book Ratio',
        'PB %',
        'Price-to-Sales Ratio',
        'PS %',
        'EV/EBITDA',
        'EV/EBITDA %',
        'EV/GP',
        'EV/GP %',
        'RV Score'
         ]
final_dataframe = pd.DataFrame(columns = my_columns)

for string in symbol_string:
    url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=advanced-stats,quote&symbols={string}&token={IEX_TOKEN}'
    data = r.get(url).json()

    for symbol in string.split(','):
        enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
        ebitda = data[symbol]['advanced-stats']['EBITDA']
        gross_profit = data[symbol]['advanced-stats']['grossProfit']
        
        try:
            ev_to_ebitda = enterprise_value/ebitda
        except TypeError:
            ev_to_ebitda = np.NaN
        
        try:
            ev_to_gross_profit = enterprise_value/gross_profit

        except TypeError:
            ev_to_gross_profit = np.NaN
            
        final_dataframe = final_dataframe.append(
                    pd.Series([
                        symbol,
                        data[symbol]['quote']['latestPrice'],
                        'N/A',
                        data[symbol]['quote']['peRatio'],
                        'N/A',
                        data[symbol]['advanced-stats']['priceToBook'],
                        'N/A',
                        data[symbol]['advanced-stats']['priceToSales'],
                        'N/A',
                        ev_to_ebitda,
                        'NA',
                        ev_to_gross_profit,
                        'na',
                        'na'

                        ],
                            index = my_columns
                        ),
                    ignore_index = True
                )
# dealing with missing data in the dataframe. we are going to replace the NA with the average for that column 

for column in ['Price-to-Earnings Ratio', 'Price-to-Book Ratio','Price-to-Sales Ratio',  'EV/EBITDA','EV/GP']:
    final_dataframe[column].fillna(final_dataframe[column].mean(), inplace = True)



# calculating the number of shares to buy
def portfolio_input():
    global portfolio
    portfolio = float(input('enter the size of your portfolio: '))

portfolio_input()
position_size = portfolio/10

       


# calculating the value %

metrics = {

'Price-to-Earnings Ratio': 'PE %',
'Price-to-Book Ratio':'PB %',
'Price-to-Sales Ratio': 'PS %',
'EV/EBITDA':'EV/EBITDA %',
'EV/GP':'EV/GP %'
}

for row in final_dataframe.index:
    for metric in metrics.keys():
        final_dataframe.loc[row,metrics[metric]] = stats.percentileofscore(final_dataframe[metric], final_dataframe.loc[row,metric])/100
        
for metric in metrics.values():
    print(final_dataframe[metric])

# Calculating the RV SCORE: The RV Score will be the arithmetic mean of the 4 percentile scores that we calculated in the last section.

for row in final_dataframe.index:
    value_percentiles = []
    for metric in metrics.keys():
        value_percentiles.append(final_dataframe.loc[row, metrics[metric]])
    final_dataframe.loc[row,'RV Score'] = mean(value_percentiles)


# sorting the 10 best stocks
final_dataframe.sort_values('RV Score', inplace = True)
# selects only the stocks with ratio greater than 0
final_dataframe = final_dataframe[final_dataframe['Price-to-Earnings Ratio'] > 0]

#saves 10 top ratio
final_dataframe = final_dataframe[:10]
final_dataframe.reset_index(inplace = True)
final_dataframe.drop('index', axis=1,inplace =True)

for i in final_dataframe.index:
    final_dataframe.loc[i,'Number of shares to buy'] =  position_size / final_dataframe.loc[i,'Price']
 
print(final_dataframe)
 
