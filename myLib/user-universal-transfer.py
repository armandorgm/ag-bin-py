import ccxt
import time
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv("secrets.env")
exchange = ccxt.binance({
        'apiKey': os.getenv("API_KEY"),
        'secret': os.getenv("SECRET"),
    })
pprint(exchange.fetch_free_balance({"type":"funding"})['USDT'])
#balance = exchange.fetch_balance({"type":"funding"})#
#pprint(balance.keys())
#pprint(balance)
def universalTransfer():
    res = exchange.sapiPostAssetTransfer({
            'type': "FUNDING_UMFUTURE",  
            'asset': 'USDT',
            'amount': 1.23,
            'timestamp': int(time.time() * 1000)
        }) 
    pprint(res)
    
""" res = exchange.unive() """