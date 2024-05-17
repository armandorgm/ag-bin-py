from dotenv import load_dotenv
from pprint import pprint
import ccxt
from ccxt import binance 
import os
import json
import logging
import time
#logging.basicConfig(level=logging.DEBUG)

# Imprime una lista de todas las clases de intercambio disponibles

symbol = 'BNBUSDT'  # Replace with your desired symbol
side = 'BUY'          # 'buy' or 'sell'
type = 'MARKET'       # 'market' or 'limit'
quantity = 0.01            # The amount of the cryptocurrency to buy/sell

    # For a market order, price parameter is not required
    #order = exchange.create_order(symbol, type, side, amount)

def main():
    load_dotenv("secrets.env")
    
    binance = ccxt.binanceusdm({
        'apiKey': os.getenv("API_KEY"),
        'secret': os.getenv("SECRET"),
        'defaultType':'future'
    })
    markets = binance.load_markets()
    #pprint(markets)
    binance.set_leverage(75,symbol)
    timestamp = int(time.time() * 1000)
    #res = binance.create_order("BNB/USDT",type,side,quantity,4,{"symbol":symbol,"side":side,"type":type,"positionSide": "LONG","timestamp":timestamp})

    #binance.set_sandbox_mode(True)  # enable sandbox mode
    #pprint(res())
    
main()
