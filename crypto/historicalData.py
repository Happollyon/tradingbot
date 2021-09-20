import requests as r 
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
import openpyxl
import datetime
import numpy as np
response = r.get(f"https://api.binance.com/api/v3/klines?symbol=HNTUSDT&interval=5m&startTime=1629547200000&limit=900").json()

my_column= [
 
"open-time",
"open",
"high",
 "low",
 "close",
 "MACD",
 "EMA26",
 "EMA12",
 "EMA9",
 "EMA6",
 "EMA3",
 "WMA",
 "BUY",
 "SELL",
 "ATR",
 "portfolio"
                                                                                                                                                                                                                 ]

df = pd.DataFrame(columns=my_column)


NaN = np.nan


def calc_ema(dataset,n):
    ema = dataset.ewm(span=n,adjust=False, ignore_na=False).mean()
    return ema
for candle in response:
    
    df = df.append(
                pd.Series([
                       datetime.datetime.utcfromtimestamp(float(candle[0])/1000),
                                       candle[1],
                                                       float(candle[2]),
                                                                       float(candle[3]),
                                                                                       float(candle[4]),
                                                                                                       'N/A',
                                                                                                                       'N/A',
                                                                                                                                       'N/A',
                                                                                                                                                       'N/A',
                                                                                                                                                                       'NA',
                                                                                                                                                                                       'NA',
                                                                                                                                                                                                       'NA',
                                                                                                                                                                                                                       NaN,
                                                                                                                                                                                                                                      NaN,
                                                                                                                                                                                                                                                     NaN,
                                                                                                                                                                                                                                                                    NaN
                   ], index = my_column
                    ), ignore_index = True
            )
df['EMA12'] = calc_ema(df['close'],12)
df['EMA26'] = calc_ema(df['close'],26)

df['EMA6'] =  calc_ema(df['close'],6)
df['EMA3'] = calc_ema(df['close'],3)
for i in range(len(df.index)):
    macd=df.loc[i,'MACD'] = df.loc[i,'EMA12'] - df.loc[i,'EMA26']

df['EMA9'] =  calc_ema(df['MACD'],9)   
wb = openpyxl.Workbook()
ws = wb.active
for r in dataframe_to_rows(df, index=False, header=True):
    ws.append(r)
wb.create_sheet('portfolio')
#ws2 = wb.get_sheet_by_name('portfolio')
wb.save('hntusdtAugust.xlsx')
