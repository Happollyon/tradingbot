import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
df = pd.read_excel('trix/01Oct2021_1757_df.xlsx', sheet_name='Sheet')
sale_df = pd.read_excel('hntusdt.xlsx', sheet_name='portfolio')
#plt.plot(df['open-time'],df['close'],label = "Price")
#plt.plot(df['open-time'],df['EMA9'],label = "Buy",color='green')
df['EMA9'] = df['MACD'].ewm(span=9,adjust = False, ignore_na=False).mean()
#df['MACD'].plot( color='green')

#ax = df['EMA9'].plot(color='r')
#df['close'].plot( ax=ax, secondary_y=True)
"""
f2 = plt.figure()
plt.plot(df['open-time'],df['MACD'])
"""
plt.scatter(df['open-time'],df['BUY'],color='purple')
plt.plot(df['open-time'],df['close'])
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()
