from asyncio import sleep
import asyncio
from decimal import Decimal
from pprint import pprint

from .interfaces.types import Order, OrderType
from .bot_strategies.concrete_strategy import EstrategiaLong,EstrategiaShort
from .bot_strategies.strategy import Strategy
from ccxt.pro import binanceusdm
#from models import BotOperation as BotOperationModel
#from dao import OrderManagerDAO
from .bot import Bot
class Bot_Operation(Bot):
    
    def __init__(self, exchange:binanceusdm, name, symbol, strategy:Strategy):
        super().__init__(name)
        self.symbol = symbol
        self.exchange = exchange
        self.strategy = strategy
        print(f"acaba de crear una operacion con nombre {name}, estrategia '{strategy}'")
    """
    def __init__1(self, 
                 exchange:binanceusdm, 
                 position_side:iPositionSide, 
                 symbol:str, 
                 threshold:float,
                 strategyName,
                 name:str) -> None:
        
        super().__init__(name)
        self.status = 0
        self.exchange = exchange
        self.entryPrice :float
        self.positionSide = position_side
        self.symbol = symbol
        self.threshold = threshold
        #self._strategy = BotOperation.getStrategy(strategyName)()
        self._strategy = EstrategiaLong()
        self.closingOrderPriceStrategy = None
        self.openingOrderAmountStrategy = None
        self.numero_ordenes_contra = 0  # Contador para las órdenes contrarias consecutivas
    """
    
    async def createOrder(self, position_side, order_side, amount, price,orderType:OrderType)->Order:
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

    def cambiar_estrategia(self, nueva_estrategia):
        self._strategy = nueva_estrategia
        print('Cambiando estrategia a:',nueva_estrategia)

    
    async def start(self):
        super().start()
        pprint(self.strategy)
        #self.exchange.verbose = True
        entryReferencePrice = (await self.exchange.watch_ticker(self.symbol))['last']
        self.entryPrice = entryReferencePrice
        pprint(entryReferencePrice)
        self.exchange.verbose = False
        while self.status:
            try:
                lastPrice = (await self.exchange.watch_ticker(self.symbol))['last']
                pprint(lastPrice)
                await self._strategy.evaluar_precio(Decimal(str(lastPrice)),self.createOrder)
            except KeyboardInterrupt:
                await self.exchange.close()
            finally:
                await asyncio.sleep(1)
                pass
        await self.exchange.close()

        
    @property
    def strategy(self) -> Strategy:
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """

        self._strategy = strategy
