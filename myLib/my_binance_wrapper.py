import pprint as pprint
import ccxt.pro as ccxtpro
import open_new_console
import asyncio
from config_manager import ConfigManager

env = ConfigManager()

class Mbw:
    def __init__(self):       
        self.exchange = ccxtpro.binanceusdm({
            'apiKey': env.api_key,
            'secret': env.secret,
            'defaultType':'future',
            'options': {
                'leverageBrackets' : None
            }
        })
        self.symbols = ["BNB/USDT","ATA/USDT"]
        print("Mbw instatiace")
    
    def getPricePrecision(self):
        if(self.exchange.market(self.symbol)):
            return self.exchange.market(self.symbol)
    
    def selectSymbol(self):
        for index, value in enumerate(self.symbols, start=1):  # Empezar el índice en 1
            print(f"{index}) {value}")  # Imprimir el menú
        selected = int(input("input a symbol number\n"))
        print("selected: " +self.symbols[selected-1])
        return self.symbols[selected-1]
        
    def selectPositionSide(self):
        positionSide=["LONG","SHORT"]
        for index, value in enumerate(positionSide, start=1):  # Empezar el índice en 1
            print(f"{index}) {value}")  # Imprimir el menú
        selected = int(input("input the positionSide number\n"))
        print("selected: " +positionSide[selected-1])
        return positionSide[selected-1]
                
    async def createOrder(self):
        try:
            min_notional = 5
            symbol = self.selectSymbol()
            pprint.pprint(self.exchange.market(symbol))
            
            book = await  self.exchange.watch_order_book(symbol,20)
            
            for i in range(20):
                print("bid:" + str(book["bids"][i][0]),"ask: " + str(book["asks"][i][0]))
            
            positionSide = self.selectPositionSide()
            
            side = 'buy' if positionSide == "LONG" else "sell"
            
            book = await  self.exchange.watch_order_book(symbol,5)
            tickPrice = float(self.exchange.market(symbol)["limits"]["market"]["min"])
            price = float(book["bids" if side =="buy" else "asks"][0][0])
            
            
            #amount = self.exchange.market(symbol)["limits"]["amount"]["min"]
            amount = self.exchange.amount_to_precision(symbol,(min_notional/price)+self.exchange.market(symbol)["limits"]["amount"]["min"] )
            print("min_amount:",amount)
            
            self.exchange.verbose = True
            
        
        #Open Order
            order = await self.exchange.create_order(symbol, "limit", side, amount, price, params={"positionSide":positionSide})
            
            order_id =int(order['id'])
            order_status = await self.exchange.fetch_order(order_id, symbol)
            pprint.pprint(order_status)
            
            # Crear una tarea asíncrona que no bloquea para monitorear la primera orden
            #task = asyncio.create_task(self.monitor_order_and_create_second(order['id'], symbol))
            
        #TakeProfitOrder
            takeProfit_side = 'sell' if side == 'buy' else 'buy'
            if takeProfit_side == 'buy':
                # Si vamos a comprar para tomar ganancias, queremos comprar más barato (un poco menos que el precio actual)
                stop_or_takeProfit_Price = float(price) / 1.002
            else:
                # Si vamos a vender para tomar ganancias, queremos vender más caro (un poco más que el precio actual)
                stop_or_takeProfit_Price = float(price) * 1.002

            # Redondear el precio según la precisión del mercado
            stop_or_takeProfit_Price = float(self.exchange.price_to_precision(symbol, stop_or_takeProfit_Price))
            takeProfitPricePlusMin = stop_or_takeProfit_Price + (1/(10**self.exchange.market(symbol)["precision"]["price"]))
            print("takeProfitPricePlusMin: ",takeProfitPricePlusMin)
            takeProfitParams = {"positionSide":positionSide}
        #    #await self.exchange.create_order(symbol, "limit", takeProfit_side, amount, stop_or_takeProfit_Price, takeProfitParams)
            open_new_console.open_new_console(
                'c:/Users/arman/myProjects/ag-bin-py/my_binance_wrapper.py', 
                str(order_id),
                str(symbol),
                "limit",
                str(takeProfit_side),
                str(amount), 
                str(stop_or_takeProfit_Price),
                str(positionSide))

            
            self.exchange.verbose = False
            await self.exchange.close()
            return order['id'], symbol, positionSide

            
        except Exception as e:
            print(e)            
            raise e
        except KeyboardInterrupt:
            pass
        finally:
            await self.exchange.close()
    
    async def monitor_order_and_create_second(self, order_id,symbol,type,side,amount,price, positionSide):
        print("monitor_order_and_create_second() started")
        try:
            while True:
                order_status = await self.exchange.fetch_order(order_id, symbol)
                if order_status['status'] == 'closed':  # Verificar que la orden se haya completado.
                    print(f"La orden {order_id} ha sido ejecutada.")
                    # Aquí se dispara el evento o se realiza una acción cuando la orden se ha completado
                    # Por ejemplo, se podría setear una variable o llamar otra función
                    #await self.create_take_profit_order(order_status)
                    await self.exchange.create_order(symbol,type,side,amount,price, {"positionSide":positionSide})
                    input("Presione Enter para cerrar...")

                    break
                else:
                    print("order_status",order_status['status'])
                await asyncio.sleep(1)  # Esperar un poco antes de volver a revisar el estado
        except Exception as e:
            print("Error en monitor_order_and_create_second:", e)
        finally:
            await self.exchange.close()

    async def create_take_profit_order(self, openOrder):
        symbol=openOrder["symbol"]
        try:
            pprint.pprint(openOrder)
            take_profit_order = await self.exchange.create_order(symbol, "limit", "sell", amount, "xxxxx", params={"positionSide": "sssssss", "reduceOnly": True})
            print(f"Orden take profit creada: {take_profit_order['id']}")
            input("Presione Enter para cerrar...2")

        except Exception as e:
            print("Error en create_take_profit_order:", e)
            input("Presione Enter para cerrar...1")

        finally:
            input("Presione Enter para cerrar...1")

    
    async def showOpenPosition(self):
        symbol = self.selectSymbol()
        #print(self.exchange.positions) #prints "None"
        #print(self.exchange.load_positions_snapshot())
        #print(self.exchange.safe_position())
        #print(await self.exchange.fetch_position(symbol))#option market only
        #print(await self.exchange.fetch_position_history(symbol))#not suported yet
        #print(await self.exchange.fetch_position_mode(symbol)) #works
        pprint.pprint(await self.exchange.fetch_position_ws(symbol))


    async def myPositions(self):
        try:
            print("Start: myPositions()")
            #res = await self.exchange.fapiPublicGetTickerPrice(params={"symbol":"BNBUSDT"})
            res = await self.exchange.fetch_positions(params={"symbol":"BNBUSDT"})
            pprint.pprint(res)
            print("End: myPositions()")

            return res
        except Exception as e:
            print("Error:" + str(e))
            raise e
        
if __name__ == "__main__":
    import sys
    '''
    symbol,type,side,amount,price, positionSide
    '''

    async def monitor_order_cli(order_id,symbol,type,side,amount,price, positionSide):
        mbw = Mbw()
        await mbw.monitor_order_and_create_second(order_id, symbol,type,side,amount,price, positionSide)

    if len(sys.argv) == 8:
        order_id = sys.argv[1]
        symbol = sys.argv[2]
        type = sys.argv[3]
        side = sys.argv[4]
        amount = sys.argv[5]
        price = sys.argv[6]
        positionSide = sys.argv[7]
        # Make sure to call the right asyncio event loop policy if needed, especially for Windows
        asyncio.run(monitor_order_cli(order_id,symbol,type,side,amount,price, positionSide))
    else:
        print("Usage: myBinanceWrapper.py <symbol>,<type>,<side>,<amount>,<price>, <positionSide>")
        sys.exit(1)