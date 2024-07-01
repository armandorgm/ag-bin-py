"""**********README
variables required
lastScale from initial price, permanentStore
"""
import asyncio
from decimal import ROUND_UP, Decimal
import simplejson as json
import math
from typing import Any, Callable, Literal, TypedDict

from ...interfaces.strategy_interface import StrategyImplementor
from ..profit_operation import Profit_Operation
from ..strategy import Strategy
from pprint import pprint
import ccxt
from...interfaces.exchange_basic import Order, iStrategy_Callback_Signal,MarketInterface,PositionSide, SymbolPrecision, ProfitOperation
#getcontext().prec = 8


class StrategyStorage(TypedDict):
    offset:str
    positionSide:str
    lastCheckpoint:str
    rootCheckpoint:str
    profit_operations:list[ProfitOperation]
    consecutives_price_fordward:int
    
class StrategyA(Strategy):
    id:int = 2
    name:str = "EstrategiaA"
    
    #def __init__(self, interface:StrategyImplementor, positionSide:PositionSide, offset:int|str|Decimal,rootCheckpoint:int|str|Decimal,lastCheckpoint:str) -> None:
    def __init__(self, interface:StrategyImplementor, data:StrategyStorage) -> None:
        super().__init__(interface)
        self.offset = Decimal(str(data["offset"]))
        self.positionSide = data["positionSide"]
        self.rootCheckpoint = Decimal(str(data["rootCheckpoint"]))
        self.lastCheckpoint = Decimal(data["lastCheckpoint"])
        self.lastPrice = Decimal(data["lastCheckpoint"])
        self._profitOperations = data["profit_operations"]
        self.lastScaleArchived = None
        self.consecutives_price_fordward = data.get("consecutives_price_fordward",0)
        print(self.__dict__)
    
    @property
    def data(self)->StrategyStorage:
        return self.interface.strategyData # type: ignore
    
    @property
    def marketData(self):
        return self.interface.marketData
    
    @property
    def cacheData(self):
        data:StrategyStorage = {
            "positionSide":str(self.positionSide),
            "offset":str(self.offset),
            "rootCheckpoint":str(self.rootCheckpoint),
            "lastCheckpoint":str(self.lastCheckpoint),
            "profit_operations":self._profitOperations,
            "consecutives_price_fordward":self.consecutives_price_fordward
        }
        pprint(data)
        return json.dumps(data)
    @property
    def previousCheckpoint(self):
        return self._getPreviousCheckpointPrice(self.lastCheckpoint)
    @property
    def nextCheckpoint(self):
        return self._getFollowingCheckpointPrice(self.lastCheckpoint)
    
    def _getFollowingCheckpointPrice(self,checkpointPrice: Decimal):
        return (checkpointPrice * self.offset).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))

    def _getPreviousCheckpointPrice(self,checkpointPrice: Decimal):
        return (checkpointPrice / self.offset).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
    def save(self):
        self.interface.saveStrategyState(self.cacheData)
        
    def updatePriceCheckpoints(self,escalas:int):
        self.lastCheckpoint*=(self.offset**escalas).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
        print(f"se actualizaron  escalas en un:{escalas} currentCheckpoint:{self.lastCheckpoint}") 
    
    def calcular_saltos_en_progresion(self, fromCheckpoint:Decimal, toNewPrice:Decimal):
        """
        [ n = \\frac{\\ln\\left(\\frac{a_n}{a_1}\right)}{\\ln®} + 1 ]
        (fórmula para el término general de una sucesión geométrica)
        (general formula for the nth term of a geometric sequence)
        """
        r = self.offset
        a_1 = fromCheckpoint
        a_n = toNewPrice
        x = a_n/a_1
        
        rawResult = (((x).ln()/(r).ln())+1)-1 # -1 to get a_1 as 0 and not as 1
        result = int(rawResult)
        return result

    
    def getNthProgresionValueFromCheckpoint(self,numero_de_saltos_de_la_progresion:int,fromCheckpointPrice:Decimal):
        value2 = fromCheckpointPrice * (self.offset**(numero_de_saltos_de_la_progresion))
        #value = self.longStrategy.currentCheckpoint*(1+self.longStrategy.offset)**numero_de_saltos_de_la_progresion
        return value2
    
    def getProfitPriceOf(self, openPrice:Decimal):
        return openPrice*self.offset
    
    @property
    def openingOrderSide(self):
        return "buy" if self.positionSide.lower() == "long" else "sell"
    @property
    def closingOrderSide(self):
        return "sell" if self.positionSide.lower() == "long" else "buy"


    
    async def isCheckpointProfitOperationActive(self, checkpoint:Decimal):
        for profit_Operation in self._profitOperations:
            #if type(profit_Operation["checkpoint"]) != type(checkpoint):
            #    raise TypeError(f"{type(profit_Operation["checkpoint"])}!={type(checkpoint)}{profit_Operation["checkpoint"]}!={checkpoint}")
            c1=Decimal(profit_Operation["checkpoint"]).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
            c2 =checkpoint.quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
            print(f"comparing {type(c1)}({c1}) and {type(c2)}({c2}))")
            #.quantize(Decimal("1e-{0}".format(self.interface.amountPrecision)),rounding=ROUND_UP)
            if c1 == c2:
                openO_task = asyncio.create_task(self.interface.fetch_order(profit_Operation["openingOrderId"]))
                closeO_task = asyncio.create_task(self.interface.fetch_order(profit_Operation["openingOrderId"]))
                
                for order in [await openO_task,await closeO_task]:
                    print(f"in for loop order:",end="")
                    pprint(order)
                    if order and order["status"] == "open":
                        return True
            else:
                print(f"checkpoint {checkpoint} not found in the list below:")
        pprint(self._profitOperations)
        return False
    
    async def evaluar_precio(self, receivedPrice:Decimal):
        escalasSobrepasadas = self.calcular_saltos_en_progresion(self.lastCheckpoint, receivedPrice)
        if escalasSobrepasadas:
            print("\n","#"*4,f"evaluar_precio starts (receivedPrice '{receivedPrice}')",f"(previous:{self.previousCheckpoint}), (currentCheckpoint:{self.lastCheckpoint}), (following:{self.nextCheckpoint})","#"*4)

            print(f"{escalasSobrepasadas} escalas sobrepasadas con respecto a la ultima actualizacion")
        
            if receivedPrice >= self.nextCheckpoint:
                print(f"current_price >= self.nextCheckpoint")
                self.consecutives_price_fordward += 1
                
                if self.consecutives_price_fordward >= 2:
                    if not (await self.isCheckpointProfitOperationActive(self.nextCheckpoint)) :
                        print(f"consecutives_price_fordward >= 2 ({self.consecutives_price_fordward >= 2})")
                        order = await self.interface.putOrder(self.positionSide, self.openingOrderSide, Decimal(self.get_min_amount(self.getMakerPrice(receivedPrice))), self.getMakerPrice(receivedPrice), "limit")
                        profitOperation:ProfitOperation = {"checkpoint":str(self.nextCheckpoint),"openingOrderId":order["info"]["clientOrderId"],"closingOrderId":None}
                        #profitOp = next((po for po in self._profitOperations if po["checkpoint"]==self.nextCheckpoint), None)
                        indice = next((i for i, po in enumerate(self._profitOperations) if po.get("checkpoint") == self.nextCheckpoint),None)
                        if indice:
                            print("indice encontrado")
                            self._profitOperations[indice] = profitOperation
                            print("operaciones modificada:",end="")
                            pprint(self._profitOperations)
                        else:
                            print("indice NO encontrado")
                            self._profitOperations.append(profitOperation)
                            print("operacion agregada",end=":")
                            pprint(self._profitOperations)

                        print(f"orden id:{order["info"]["clientOrderId"]}")
                        #pending_profit_operation = self.interface.create_pending_operations(order["id"],order["amount"],order["info"]["positionSide"], float(order["price"]), order["fee"],self.getProfitPriceOf(Decimal(str(order["price"]))))
                    else:
                        print("self.isCheckpointProfitOperationActive == True")
                else:
                    print(f"self.consecutives_price_fordward is >= 2 ({self.consecutives_price_fordward >= 2})")
                self.updatePriceCheckpoints (escalasSobrepasadas)
                
                                
            elif receivedPrice <=self.previousCheckpoint:
                self.consecutives_price_fordward = 0
                self.updatePriceCheckpoints (escalasSobrepasadas)
            
            self.lastScaleArchived = escalasSobrepasadas
            self.save()

        else:
            if self.lastScaleArchived != 0:
                print("checkpoint not reached ")
                self.lastScaleArchived = 0
            else:
                if receivedPrice > self.lastPrice:
                    print(end="\u2191",flush=True)#\u25B2 for ▲
                elif receivedPrice < self.lastPrice:
                    print(end="\u2193",flush=True)# \u25BC ▼
                else:
                    print(end="·",flush=True)
        self.lastPrice = receivedPrice# 

    def getMakerPrice(self,currentPrice:Decimal):
        tick = 1/(Decimal(10)**self.interface.pricePrecision)
        if tick > currentPrice:
            raise ValueError(f"tick({tick}) cant be greater than price({currentPrice}). in Method StrategyA.getMakerPrice()")
        #print("tick=",tick)
        if self.positionSide.lower() == "long":
            return currentPrice+(tick*(-1))
        elif self.positionSide.lower() == "short":
            return currentPrice+(tick)
        else:
            raise BaseException("Position Side Unknown")

    async def onOpenOrderExecution(self, orderData: Order):
        pprint(orderData)
        if orderData["amount"]:
            await self.interface.putOrder(orderData["info"]["positionSide"],self.closingOrderSide,Decimal(orderData["amount"]), self.getProfitPriceOf(Decimal(str(orderData["price"]))), "limit")

    async def onCloseOrderExecution(self, orderData: Order) -> None:
        pprint(orderData)
        if orderData["amount"]:
            await self.interface.putOrder(orderData["info"]["positionSide"],self.openingOrderSide, Decimal(orderData["amount"]), self.getProfitPriceOf(Decimal(str(orderData["price"]))), "limit")

