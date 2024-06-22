from asyncio import sleep
import asyncio
from decimal import Decimal
from pprint import pprint

from .bot_strategies.strategy_a.strategyA import StrategyA

from .interfaces.types import Num, Order, OrderType
from .bot_strategies.concrete_strategy import EstrategiaLong,EstrategiaShort
from .bot_strategies.strategy import Strategy
from ccxt.pro import binanceusdm
#from models import BotOperation as BotOperationModel
#from dao import OrderManagerDAO
from .bot import Bot
class Bot_Operation(Bot):
    
    def __init__(self, exchange:binanceusdm, name, symbol, strategy:StrategyA):
        super().__init__(name)
        self.symbol = symbol
        self.exchange = exchange
        self.strategy = strategy
        print(f"acaba de crear una operacion con nombre {name}, estrategia '{strategy}'")
    
    async def createOrderBackSignal(self, position_side, order_side, amount, price,orderType:OrderType)->Order:
        print("se colocará una orden:",self.symbol,orderType,f"##{order_side}##",amount, price, {"positionSide":position_side})
        self.exchange.verbose = True
        try:
            order = await self.exchange.create_order(self.symbol,'limit',order_side,amount,price,{"positionSide":position_side})
        finally:
            self.exchange.verbose = False
        return order    

    def abrir_orden(self, tipo, precio_actual):
        self.precio_entrada = precio_actual
        print(f'Abrir {tipo} a precio {precio_actual}')
        
    def cerrar_orden(self):
        print('Cerrar orden actual')
    
    async def start(self):
        super().start()
        pprint(self.strategy)
        #self.exchange.verbose = True
        entryReferencePrice = (await self.exchange.watch_ticker(self.symbol))['last']
        self.entryPrice = entryReferencePrice
        pprint(f"entryReferencePrice:{entryReferencePrice}, offset:{self.strategy.offset*100}%")
        self.exchange.verbose = False
        tailPrice = entryReferencePrice
        while self.status:
            try:
                lastPrice = Decimal(str((await self.exchange.watch_ticker(self.symbol))['last']))
                if not tailPrice == lastPrice:
                    tailPrice=lastPrice
                    await self.strategy.checkPendingOrdersToClose(self.symbol,lastPrice,self.exchange.fetch_order)
                    await self.strategy.evaluar_precio(lastPrice, self.createOrderBackSignal)
            except KeyboardInterrupt:
                await self.exchange.close()
            finally:
                await asyncio.sleep(1)
                pass
        await self.exchange.close()


