from asyncio import sleep
import asyncio
from decimal import Decimal
from pprint import pprint
from typing import Any, List, Literal
from ccxt.pro import binanceusdm
import ccxt

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

            pprint(botStrategyConfig)
            if strategy.__dict__["id"] == botStrategyConfig.strategy_id:
                print("botStrategyConfig found:")
                pprint(botStrategyConfig.data)
                data = Strategy.from_json(botStrategyConfig.data)
                return strategy(self, **data) # type: ignore
        raise Exception("Not yet implemented")
    
    def saveStrategyState(self, strategyState):
        pprint(strategyState)
        self.dao.saveStrategyState(self.botId, strategyState)
        
    async def putOrder(self, position_side, order_side, amount, price,orderType:OrderType)->Order:
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
                    await self.checkPendingOrdersToClose(lastPrice)
                    await self.strategy.evaluar_precio(lastPrice)
            except KeyboardInterrupt:
                await self.exchange.close()
            finally:
                await asyncio.sleep(1)
                pass
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
        print("pricePrecisionType:", type(value))
        return value

    

                    
    
