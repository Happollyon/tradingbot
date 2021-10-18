# book strategy
import ta
import requests as r
import pandas as pd
import numpy as np
import websocket
import json
from playsound import playsound
import datetime
from binance.spot  import Spot
import config
# import keys
BINANCE_KEY= config.BINANCE_KEY
BINANCE_SECRET_KEY = config.BINANCE_SECRET_KEY
#creates client obj
client = Spot(key=BINANCE_KEY,secret = BINANCE_SECRET_KEY)

symbolss = ['BTCUSDT','ETHUSDT','BNBUSDT','ADAUSDT','XRPUSDT','SOLUSDT','DOTUSDT','DOGEUSDT','LTCUSDT','LINKUSDT','AVAXUSDT','ALGOUSDT','SHIBUSDT','MATICUSDT','XLMUSDT','ATOMUSDT','ETCUSDT','FTTUSDT','THETAUSDT','XTZUSDT','HBARUSDT','XMRUSDT','FTMUSDT','EGLDUSDT','CAKEUSDT','EOSUSDT','NEARUSDT','KLAYUSDT','AAVEUSDT','XECUSDT','GRTUSDT','QNTUSDT','WAVESUSDT','NEOUSDT','KSMUSDT','MKRUSDT','BTTUSDT','ONEUSDT','HNTUSDT','DASHUSDT','OMGUSDT','CELOUSDT','CHZUSDT','RUNEUSDT','ARUSDT','COMPUSDT','DCRUSDT','ZECUSDT','HOTUSDT','XEMUSDT','TFUELUSDT','SUSHIUSDT','MANAUSDT','ICXUSDT','ENJUSDT','YFIUSDT','BTGUSDT','QTUMUSDT','DYDXUSDT','CRVUSDT','PERPUSDT','ZILUSDT','MINAUSDT','SNXUSDT','FLOWUSDT','RENUSDT','BATUSDT','SRMUSDT']
symbols =['BTCUSDT','ETHUSDT']
stocks = {}
sentinels={}
order=[]

def place_order(symbol,side,typee,quantity,timeInForce,price):
    symbol = symbol.upper()
    params = {
    "symbol": symbol,
    "side": side,
    "type": typee,
    "quantity": quantity,
    "timeInForce":timeInForce,
    'price':price
    }
    response = client.new_order(**params)
    print(response)
    return response


def get_pastData(symbol,interval): # requesting previous candes
    symbol =symbol.upper()
    data = r.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100").json()
    return data


def calc_change(old,new):
    change = ((new-old)/old)*100
    return round(change,3)

my_columns = [
        'time',
        'open',
        'high',
        'low',
        'price',
        'ema26',
        'ema12',
        'macd',
        'signal',
        'rsi',
        'portfolio',
        'buy',
        'sell',
        'sarDOWN',
        'sarUP'
        ]


"""
GLOBAL VARIABLES
"""
filled = True
fill_side = 'BUY'
position = False
fees=0
profit=0
payed = 0
step_size=0
tick_size=0
qty = 0
portfolio=float(input('portfolio: '))
sentinelsN = int(input('how many sentinels?: '))
sentinels={}
for i in range(sentinelsN):
    size  = (portfolio*0.9)/sentinelsN
    sentinels[i]={
            'name':'',
            'size':size,
            'position':False
            }
for i in range(len(sentinels)):
    print(sentinels[i])
orderID = 0

def create_dataFrame(data_set):
    
    # creates data frame
    #graph =  pd.DataFrame(columns = my_columns)
    df = pd.DataFrame(columns = my_columns)

    # creates a NaN to avoid errors
    NaN = np.nan
    # populates dataframe
    for candle in data_set:

        df = df.append(
            pd.Series([
                datetime.datetime.utcfromtimestamp(float(candle[0])/1000),
                candle[1],
                float(candle[2]),
                float(candle[3]),
                float(candle[4]),
                NaN,
                NaN,
                NaN,
                NaN,
                NaN,
                NaN,
                NaN,
                NaN,
                NaN,NaN
                ],
                    index=my_columns
                ),
            ignore_index = True

            )
    return df

def buy(price):
    
    global position
    global payed
    global profit
    global df
    global portfolio
    global qty
    global symbol
    global step_size
    global tick_size
    global fill_side
    global orderID
    global filled
    
    signal = df['signal'].iloc[-1]
    macd = df['macd'].iloc[-1]
    rsi = df['rsi'].iloc[-1]
    qty = portfolio / price
    qty = round(qty,step_size)
    
    if position == False and 1>3 and filled == True:
        
        profit = price + (price*0.001)
        profit = round(profit,tick_size)
        payed = price-(price*0.001)
        payed = round(payed,tick_size)
        print(profit,payed)
        response = place_order(symbol,'BUY','LIMIT',qty,'GTC',payed)   
        
        if response['status'] == 'FILLED':
            position = True
            filled = True
    
            print(f"""
            ----------------------------------
            ************* BUY ***************
            ----------------------------------
            
            price: $ {price}
            
            profit: $ {profit}
             
            qty: {qty}
            ==================================
            """)
        else:
            print('here')
            fill_side = 'BUY'
            filled = False
            orderID = response['orderId']

def is_filled(orderID,side):#function is called till order is filled (every second)
    global position
    global filled
    print('checking..')
    order = client.get_order(symbol.upper(),orderId=orderID)
   
    if order['status'] == 'FILLED':
        price = order['price']
        if side =='BUY':
            position = True
            filled = True
            print(f"""
            ----------------------------------
            ***************BUY****************
            ----------------------------------

            price: $ {price}

            profit: $ {profit}

            qty: {qty}

            ==================================
            """) 
        else:
            
            position = False
            filled = True
            change = calc_change(payed,profit)
            print(f"""
            -----------------------------------
            ############# SELL ################
            -----------------------------------
            price: $ {profit}
            
            {change}%    
            
            ===================================
            """)

       
def sell():
    global position
    global payed
    global profit
    global qty
    global symbol
    global fill_side
    global filled
    global orderID
    change = calc_change(payed,profit)
    
    response = place_order(symbol,'SELL','LIMIT',qty,'GTC',profit)
   
    if response['status'] == 'FILLED':
        filled=True
        print(f"""
            -----------------------------------
            ############# SELL ################
            -----------------------------------
            price: $ {profit}
            
            {change}%    
            
            ===================================
            """)
    else:
        
        orderID = response['orderId']
        fill_side='SELL'
        filled = False

def on_message(ws,message):
    global df
    global position
    global portfolio
    message  = json.loads(message)
    print(message['k']['x'])
    if filled == False:
        is_filled(orderID,fill_side)
    
    if position ==True:
        sell()

    if message['k']['x'] == True:
        s=message['s']
        df = stocks[s]['df']
        NaN = np.nan
        size = len(df.index)
        time = datetime.datetime.utcfromtimestamp(message['E']/1000)
        data = message['k']
        df.loc[size] = [time,float(data['o']),float(data['h']),float(data['l']),float(data['c']),NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN,NaN]
        #df['macd'] = ta.trend.MACD(df['price']).macd()
        #df['signal'] = ta.trend.MACD(df['price']).macd_signal()
        df['rsi'] = ta.momentum.StochRSIIndicator(df['price'])              
        df['sarUP'] = ta.trend.PSARIndicator(df['high'],df['low'],df['price']).psar_up()]
        buy(float(data['c']))

def on_close(ws, message):
    print('CONECTION CLOSED BY BINANCE')

def trade():
    
    global step_size
    global tick_size
    
    for symbol in symbols:
        pastDATA = get_pastData(symbol,'1m')

        df = create_dataFrame(pastDATA)
        symbol_info = r.get(f'https://api.binance.com/api/v3/exchangeInfo?symbol={symbol.upper()}').json()
        
        for filt in symbol_info['symbols'][0]['filters']:
            if filt['filterType'] == 'LOT_SIZE':
                step_size = filt['stepSize'].find('1') - 2
                if step_size<0:
                    step_size=0
                
            if filt['filterType']=='PRICE_FILTER':
                tick_size = filt['tickSize'].find('1')-2
                if tick_size<0:
                    step_size=0
                
        
        #df['macd'] = ta.trend.MACD(df['price']).macd()
        #df['signal'] = ta.trend.MACD(df['price']).macd_signal()
        df['rsi'] = ta.momentum.StochRSIIndicator(df['price'])
        #df['sarDOWN'] = ta.trend.PSARIndicator(df['high'],df['low'],df['price']).psar_down()
        df['sarUP'] = ta.trend.PSARIndicator(df['high'],df['low'],df['price']).psar_up()    
        
        stocks[symbol] = {
                'position':False,
                'buy_price':0,
                'tick_size':tick_size,
                'step_size':step_size,
                'df':df
                }
        
    url = f'wss://stream.binance.com:9443/ws/'
    url = url + '@kline_1m/'.join(symbols)+'@kline_1m'
    url = url.lower() 
    for stock in stocks:
        print(len(stocks[stock]['df']))
    #url = f'wss://stream.binance.com:9443/ws/{symbol}@kline_1m'
    ws= websocket.WebSocketApp(url, on_message=on_message,on_close=on_close)
    ws.run_forever()

trade()   



