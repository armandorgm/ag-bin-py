from user_interface import UserInterface
import ccxt.pro as ccxtpro
import ccxt
import asyncio
from pprint import pprint
import open_new_console
import utils
from order_manage_dao import OrderManagerDAO
from ccxt.base.types import OrderType,OrderSide,PositionSide,Order

class OrderManager:
    def __init__(self, api_key: str, secret: str, user_interface: UserInterface):
        self.dao = OrderManagerDAO("order_manager.db")
        self.exchange = ccxtpro.binanceusdm({
        'apiKey': api_key,
        'secret': secret,
        'defaultType':'future',
        'options': {
            'leverageBrackets' : None
        }
    })  
        #self.exchange.set_sandbox_mode(True)
        self.market = asyncio.create_task(self.exchange.load_markets())
        self.user_interface = user_interface
        self.symbols = ["BNB/USDT","ATA/USDT","TRX/USDT"]
        print("exchange instatiace")
        self.open_orders = []

    async def startMenu(self):


        try:
            option=None
            while option !=str(0):
                print("1) print my Positions")
                print("2) createOrder")
                print("3) showOpenPosition")
                print("4) orderStatus")
                print("5) openTakeMinProfit")
                print("6) Create new bot Operation")
                print("0) Exit")
                option = input("write a number from menu\n")
                match option:
                    case "1":
                        #print(exchange.markets)
                        #exchange.exchange.verbose = True  
                        await self.myPositions()
                    case "2":
                        order_result = await self.createOrder()
                    case "3":
                        await self.showOpenPosition()
                    case "4":
                        await self.orderStatus()
                    case "5":
                        await self.openTakeMinProfit()
                    case "6":
                        await self.createNewBotOperation()
                    case "99":
                        await self.testFuction()
                    case "0":
                        print("Exiting the menu...")
                        break  # Salir del bucle
                    case _:
                        print("Invalid option, please try again.")                        
                print("#"*100)
        except Exception as e:
            print("Error en main()" + str(e.args))
            raise e
        except KeyboardInterrupt:
            pass
        finally:
            await self.exchange.close()
            
    async def monitor_order(self, order_id, symbol):
        raise "not implemented monitor_order yet"
    
    def getPricePrecision(self):
        if(self.exchange.market(self.symbol)):
            return self.exchange.market(self.symbol)
  
        
    async def orderStatus(self):
        symbol = self.selectSymbol()
        order_id = input("ingrese el id de la orden")
        order_status = await self.exchange.fetch_order(order_id,symbol)
        pprint.pprint(order_status)
     
    async def openTakeMinProfit(self):
        order_id = "55928602627"
        #order_status = await self.exchange.fetch_order_status(order_id)#need symbol
        #orders = await self.exchange.fetch_orders(self.user_interface.select_symbol() )#works
        #pprint(orders)
     
     
    async def getMinAmountAtMarketPrice(self,symbol,side:OrderSide) -> int:
        await self.market
        min_notional = 5
        book = await self.exchange.watch_order_book(symbol,5)
        price = float(book["asks" if side =="buy" else "bids"][0][0])

        return self.exchange.amount_to_precision(symbol,(min_notional/price)+self.exchange.market(symbol)["limits"]["amount"]["min"] )
 
    async def testFuction(self):
        order_id = "55928602627"
        symbol = "BNB/USDT"
        order = await self.exchange.fetch_order(order_id,symbol)
        pprint(order)
        await self.createOpositeOrder(order)
        

        
    async def createOpositeOrder(self, order:Order)->Order:
        pprint(order["symbol"])
        pprint(order["type"])
        pprint(order["side"])
        pprint(order["amount"])
        pprint(order["price"])
        opositeSide = 'sell' if order["side"] == 'buy' else 'buy'
        opositePositionSide:PositionSide = "short" if str(order["info"]["positionSide"]).lower() == "long" else "long"

        return await self.createOrderV2(order["symbol"],order["type"],opositeSide,order["amount"],order["price"],opositePositionSide)
 
    async def createNewBotOperation(self):
            symbol = self.user_interface.select_symbol()
            market = await self.market
            symbolData = self.exchange.market(symbol)
            pprint(symbolData)
            positionSide = self.user_interface.selectPositionSide()
            
            #minimalAmount = self.exchange.amount_to_precision(symbol,(5/price)+self.exchange.market(symbol)["limits"]["amount"]["min"] )
            if positionSide == "BOTH":
                startingOrder = await self.createOrderV2(symbol,"market", "buy", await self.getMinAmountAtMarketPrice(symbol,"buy"),None,"long")
                await self.createOpositeOrder(startingOrder)
    
    async def createOrder(self):
        
        try:
            symbol=""
            type=""
            side = ""
            amount = ""
            price = ""
            positionSide=""
  
            symbol = self.user_interface.select_symbol()
            taskWatchOrderBook = asyncio.create_task (self.exchange.watch_order_book(symbol,5))
            positionSide = self.user_interface.selectPositionSide()       
            

            await taskWatchOrderBook
            book = await  self.exchange.watch_order_book(symbol,5)
          
            side = 'buy' if positionSide == "LONG" else "sell"
            min_notional = 5
            
            #pprint(self.exchange.market(symbol))
            
            for i in range(1):
                print("bid:" + str(book["bids"][i][0]),"ask: " + str(book["asks"][i][0]))
          
            tickPrice = float(self.exchange.market(symbol)["limits"]["market"]["min"])
            price = float(book["bids" if side =="buy" else "asks"][0][0])
            
            
            #amount = self.exchange.market(symbol)["limits"]["amount"]["min"]
            amount = self.exchange.amount_to_precision(symbol,(min_notional/price)+self.exchange.market(symbol)["limits"]["amount"]["min"] )
            print("min_amount:",amount)
            
            self.exchange.verbose = True
            
        
        #Open Order
            order = await self.exchange.create_order(symbol, "limit", side, amount, price, params={"positionSide":positionSide})
            return order
            self.lastOrder = order
            
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
    
    async def createOrderV2(self, symbol, type:OrderType, side:OrderSide, amoung:float, price:float, positionSide:PositionSide) -> Order:
                                   
            self.exchange.verbose = True     
            order = await self.exchange.create_order(symbol, type, side, amoung, price, params={"positionSide":positionSide})
            self.exchange.verbose = False
            return order
    
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
            pprint(res)
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
        orderManager = OrderManager()
        await orderManager.monitor_order_and_create_second(order_id, symbol,type,side,amount,price, positionSide)

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