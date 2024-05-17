# -*- coding: utf-8 -*-

import sys
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv("secrets.env")
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt  # noqa: E402

print('CCXT Version:', ccxt.__version__)

exchange = ccxt.binance({
     'apiKey': os.getenv("API_KEY"),
        'secret': os.getenv("SECRET"),
    'options': {
        'defaultType': 'future',
    },
})

exchange.set_sandbox_mode(True)  # comment if you're not using the testnet
markets = exchange.load_markets()
exchange.verbose = True  # debug output

balance = exchange.fetch_balance()
positions = balance['info']['positions']
pprint(positions)