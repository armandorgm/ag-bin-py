from asyncio import sleep
import asyncio
from decimal import Decimal
import json
from pprint import pprint
from typing import Any, List, Literal, Optional
from ccxt.pro import binanceusdm
import ccxt
from .utils import Utilidades

from .bot_strategies.profit_operation import Profit_Operation

from .sql_models.models import strategy_config_model

from .bot import Bot

from .interfaces.strategy_interface import StrategyImplementor
from .interfaces.bot_dao_interface import bot_dao_interface
from .interfaces.types import FeeInterface, Num, Order, OrderType

from .bot_strategies.strategy import Strategy

class Bot_Operation(Bot, StrategyImplementor):

    def __init__(self, botId:int,exchange:binanceusdm,dao:bot_dao_interface, symbol, strategies:List[Strategy],strategyConfigId:int, description:str|None=None):
        super().__init__(description)
        self.strategies = strategies
        self.botId = botId
        self.symbol = symbol
        self.exchange = exchange
        self.dao = dao
        self.strategyConfigId = strategyConfigId
        botStrategyConfig = self.dao.getBotStrategyConfig(self.strategyConfigId)
        if not botStrategyConfig:
            raise Exception(f"botStrategyConfig id={self.strategyConfigId} Not found")
        self.strategy = self.loadBotStrategy(botStrategyConfig)
        print(f"acaba de instanciar una operacion con nombre {description}")
    
    @property
    def marketData(self):
        return self.exchange.market(self.symbol)
    
    def loadBotStrategy(self,botStrategyConfig:strategy_config_model )->Strategy:
        
        for strategy in self.strategies:

            if strategy.__dict__["id"] == botStrategyConfig.strategy_id:
                dataJson = Strategy.from_json(botStrategyConfig.data)
                #tupleData = tuple(dataJson.values())
                return strategy(self, dataJson) # type: ignore

        if not len(self.strategies) > 0:
            raise Exception("Empty EstrategyList loaded")
        raise Exception("Not yet implemented")
    
    def saveStrategyState(self, strategyState):
        result = self.dao.saveStrategyState(self.botId, strategyState)
    @property
    def idUnico(self)->str:
        return Utilidades.generarIdUnico()
    
    async def putOrder(self,newClientOrderId, position_side, order_side, amount, price, orderType):
        print("se colocará una orden:",self.symbol,orderType,f"##{order_side}##",amount, price, {"positionSide":position_side})
        print(f"ordenIdGenerado:{newClientOrderId}")
        if position_side.lower() == "long" and order_side.lower() == "buy" or \
        position_side.lower() == "short" and order_side.lower() == "sell":
            print("putOrder recibio an IN order")
        else:
            print("putOrder recibio a OUT order")
        self.exchange.verbose = True
        #self.dao.registerOpenOperation()#NotImplemented Yet
        try:
            order = await self.exchange.create_order(self.symbol, orderType, order_side, float(amount), price, {"positionSide":position_side,"newClientOrderId":newClientOrderId})
        except ccxt.OperationFailed as e:
            print(e)
            print("ERROR colocando la Orden", "ccxt.OperationFailed")
            print(e)
            raise e
            
        finally:
            self.exchange.verbose = False
        return order    
    
    
        
    async def watchOrders(self):
        
        while self.status:
            orders = await self.exchange.watch_orders(symbol=self.symbol)
            for order in orders:
                task = asyncio.create_task(self.strategy.onOrderUpdate(order))
                
    async def startMonitorWs(self):
        asyncio.create_task(self.watchOrders())

    
    async def start(self):
        super().start()
        #self.exchange.verbose = True
        #entryReferencePrice = (await self.exchange.watch_ticker(self.symbol))['last']
        ticker = (await self.exchange.fetch_ticker(self.symbol))
        entryReferencePrice = ticker['last']
        
        await self.strategy.preInit(ticker)
        await self.startMonitorWs()
        self.exchange.verbose = False
        tailPrice = entryReferencePrice
        lastPrice = Decimal(str((await self.exchange.watch_ticker(self.symbol))['last']))
        self.exchange.enableRateLimit =False
        while self.status:
            try:
                lastPrice = Decimal(str((await self.exchange.watch_ticker(self.symbol))["last"]))
                if not tailPrice == lastPrice or True:
                    tailPrice=lastPrice
                    #await self.checkPendingOrdersToClose(lastPrice)
                    
                    asyncio.create_task( self.strategy.evaluar_precio(lastPrice))
            except KeyboardInterrupt:
                await self.exchange.close()
            finally:
                await asyncio.sleep(0.5)
        await self.exchange.close()

    def create_pending_operations(self, exchangeId: str, amount: None | str | float | int | Decimal, position_side: Literal['long'] | Literal['short'], entry_price: float, open_fee: FeeInterface | None, closing_price: Decimal) -> Profit_Operation:
        raise NotImplementedError

    def get_pending_operations(self) -> List[Profit_Operation]:
        return self.dao.get_pending_operations_for_bot(self.botId)


    async def checkPendingOrdersToClose(self,current_price:Decimal):
            """
            Revisar si hay ordenes por cerrar
            """
            pending_close_profit_operation_list = self.dao.get_pending_operations_for_bot(self.botId)
            print("Ordenes pendientes por cerrar:", len(pending_close_profit_operation_list))
            for pending_profit_operation in pending_close_profit_operation_list:
                try:
                    orderData:Order = await self.exchange.fetch_order(pending_profit_operation.exchangeId,self.symbol)
                except Exception as e:
                    print(e)
                    continue
                print(orderData["status"])
                if orderData["status"] == "closed": #before pending_profit_operation.check_price(current_price)
                    #print(f"Precio de cierre de operacion alcanzado ({pending_profit_operation.close_price})")
                    order_side = "sell"
                    try:
                        order = await self.putOrder(pending_profit_operation.position_side, order_side, pending_profit_operation.amount,pending_profit_operation.close_price,"limit") # type: ignore
                        if order["id"]:
                            print(f"ORDEN DE CIERRE ID({order["id"]}) COLOCADA")
                    except ccxt.NetworkError as e:
                        print('fetch_order_book failed due to a network error:', str(e))
                        # retry or whatever
                    except ccxt.ExchangeError as e:
                        print('fetch_order_book failed due to exchange error:', str(e))
                        # retry or whatever
                    except Exception as e:
                        print('fetch_order_book failed with:', str(e))
                        # retry or whatever
                    finally:
                        self.dao.delete_pending_operations(pending_profit_operation.id)
                        
                else:#si la condicion no se cumple guardar la operacion
                    print(f"Precio de cierre de operacion NO alcanzado ({pending_profit_operation.close_price})")
    
    @property
    def tick(self)->Decimal:
        return self.prec

    
    @property
    def notionalMin(self)->Decimal:
        minNotionalFilter = self.marketData["info"]["filters"][5]
        if minNotionalFilter["filterType"] == "MIN_NOTIONAL":
            return Decimal(minNotionalFilter["notional"])
        raise BaseException(f"Wrong index to get filterType(MIN_NOTIONAL). Actual({minNotionalFilter["filterType"]})")
    
    @property
    def amountPrecision(self)->int:
        return self.marketData["precision"]["amount"]

    @property
    def pricePrecision(self)->int:
        value = self.marketData["precision"]["price"]
        return value

    @property
    def strategyData(self) -> dict:
        res = self.dao.getBotStrategyConfig(self.botId)
        if res:
            return json.loads(res.data)
        raise Exception("not getBotStrategyConfig found in dao.getBotStrategyConfig()")

    async def fetch_order(self,orderId):
        return await self.exchange.fetch_order(orderId,self.symbol,{"origClientOrderId":orderId})

    

                    
    
