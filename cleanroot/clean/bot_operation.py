from asyncio import sleep
import asyncio
from decimal import Decimal
from pprint import pprint
from typing import Any, List
from ccxt.pro import binanceusdm

from .bot import Bot

from .interfaces.strategy_interface import StrategyImplementor
from .interfaces.bot_dao_interface import bot_dao_interface
from .interfaces.types import Num, Order, OrderType

from .bot_strategies.strategy import Strategy

class Bot_Operation(Bot,StrategyImplementor):
    
    def __init__(self, botId:int,exchange:binanceusdm,dao:bot_dao_interface, symbol, strategies:List[Any],strategyConfigId:int, description:str|None=None):
        super().__init__(description)
        Bot_Operation.strategies = strategies
        self.botId = botId
        self.symbol = symbol
        self.exchange = exchange
        self.dao = dao
        self.strategyConfigId = strategyConfigId
        self.strategy = self.loadBotStrategy()
        print(f"acaba de crear una operacion con nombre {description}, estrategia '{strategy}'")
    
    @property
    def marketData(self):
        return self.exchange.market(self.symbol)
    
    def loadBotStrategy(self)->Strategy:
        botStrategyConfig = self.dao.getBotStrategyConfig(self.strategyConfigId)
        if not botStrategyConfig:
            raise Exception(f"botStrategyConfig id={self.strategyConfigId} Not found")
        
        for strategy in Bot_Operation.strategies:

            pprint(botStrategyConfig)
            if strategy.__dict__["id"] == botStrategyConfig.strategy_id:
                print("botStrategyConfig found:")
                pprint(botStrategyConfig.data)
                return strategy(strategy.                        parseStrategyData(botStrategyConfig.data)
        raise Exception("Not yet implemented")
    
    def saveStrategyState(self, strategyState):
        pprint(strategyState)
        self.dao.saveStrategyState(self.botId, strategyState)
        
    async def createOrderBackSignal(self, position_side, order_side, amount, price,orderType:OrderType)->Order:
        print("se colocará una orden:",self.symbol,orderType,f"##{order_side}##",amount, price, {"positionSide":position_side})
        self.exchange.verbose = True
        self.dao.registerOpenOperation(self.botId)
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
        print(f"symbol======{self.symbol}\n",self)
        print(self)
        print(f"symbol======{self.symbol}\n",self)
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


