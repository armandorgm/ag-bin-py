import ccxt
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv("secrets.env")
exchange = ccxt.binance({
        'apiKey': os.getenv("API_KEY"),
        'secret': os.getenv("SECRET"),
    })
pprint(exchange.fetch_free_balance())
exchange.sapi_post_futures_transfer
balance = exchange.fetch_balance({"type":"funding"})#
pprint(balance.keys())
pprint(balance)