import ccxt.pro as ccxtpro
import asyncio
from asyncio import run
import signal
import os
from dotenv import load_dotenv
load_dotenv("secrets.env")

async def main():
    
    # Configurar el manejador de señales
    exchange = ccxtpro.binanceusdm({
        'apiKey': os.getenv("API_KEY"),
        'secret': os.getenv("SECRET"),
        'newUpdates': False})
    try:
        count = 0
        while count < 55:
            count = count + 1
            res = await exchange.watch_trades("BNB/USDT",None,1)
            #print(res)
            #print(orderbook['asks'][0], orderbook['bids'][0])
            #await exchange.sleep (1000) # every 100 ms
            print(str(count) + "\t", exchange.iso8601(exchange.milliseconds()), res,"\n\n")
    except Exception as e:
        print(e)        
    except KeyboardInterrupt:
        pass
    finally:
        print("cerrando la conexion")
        await exchange.close()
    await exchange.close()


run(main())