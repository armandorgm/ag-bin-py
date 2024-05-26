# main.py
#import ccxt
import os
import time
from tkinter import scrolledtext
from dotenv import load_dotenv
import json
import asyncio

#The library supports concurrent asynchronous mode with asyncio and async/await in Python 3.7.0+

#import ccxt.async_support as ccxt # link against the asynchronous version of ccxt
import ccxt as ccxt

def body(binance:ccxt.binanceusdm,markets):    
    count = 0
    while count >1:
        try:
            count=count+1
            #orderbook = binance2.watch_balance("BNBUSDT", 5)
            orderbook = binance.watch_balance()
            
            #print(orderbook)  # Print every update
        except Exception as e:
            print(e)
            # raise e
        
    
    #binance.watch_ticker("BNBUSDT")    

    
    #text_widget = tk.Text(ventana, wrap=tk.WORD)
    #text_widget.pack()
    #formatted_data = "\n".join(markets.keys())
    #text_widget.insert(tk.END, formatted_data)
    
    balance = binance.fetch_balance()
    #print(balance["USDT"])
    
    #positions = balance['info']['positions']
    #print(positions[0])
    
    #print("positions",positions.keys())
    
    # Posicionar la etiqueta en la ventana

    #print(positions)
    #consola.insert(tk.END, positions)
    #consola.yview(tk.END)
    

    # Formatea los datos de los mercados (markets_data) como una cadena
    #open_orders = binance.fetch_open_orders("BNBUSDT",None,None,{"timestamp":binance.milliseconds ()})
    open_orders = binance.fetch_open_orders("BNBUSDT")
    print(open_orders)
    
    open_positions = binance.fetch_positions(["BNBUSDT"])
    print(open_positions)
    
    



    


    #root.attributes("-fullscreen","true")

def main():
    load_dotenv("secrets.env")
    
    binance = ccxt.binanceusdm({
        'apiKey': os.getenv("API_KEY"),
        'secret': os.getenv("SECRET"),
        'defaultType':'future'
    })
    markets = binance.load_markets()

    body(binance,markets)


if __name__ == "__main__":
    main()
