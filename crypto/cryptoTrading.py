""" 
    Fagner Nunes 07/2021
    trading bot unsing binance API
"""


import numpy as np
import pandas as pd 
import requests as r  
import os

BINANCE_KEY = os.environ["BINANCE_KEY"]
BINANCE_SECRET = os.environ.get("BINANCE_SECRET")
print(BINANCE_KEY)
