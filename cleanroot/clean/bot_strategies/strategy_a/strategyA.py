"""**********README
variables required
lastScale from initial price, permanentStore
"""
import asyncio
from decimal import ROUND_UP, Decimal
import json
import math
from typing import Any, Callable, Literal

from .types import CheckpointReachMessage
from ...interfaces.strategy_interface import StrategyImplementor
from ..profit_operation import Profit_Operation
from ..strategy import Strategy
from pprint import pprint
import ccxt
from...interfaces.exchange_basic import Order, iStrategy_Callback_Signal,MarketInterface,PositionSide, SymbolPrecision
#getcontext().prec = 8

class StrategyA(Strategy):
    id:int = 2
    name:str = "EstrategiaA"
    
    #def __init__(self, interface:StrategyImplementor, positionSide:PositionSide, offset:int|str|Decimal,rootCheckpoint:int|str|Decimal,lastCheckpoint:str) -> None:
    def __init__(self, interface:StrategyImplementor, **data:dict) -> None:
        super().__init__(interface)
        self.offset = Decimal(str(offset))
        self.consecutives_price_fordward = 0
        self.positionSide = positionSide
        self.rootCheckpoint = Decimal(str(rootCheckpoint))
        self.lastCheckpoint = Decimal(lastCheckpoint)
        self.checkpointMemory= None
        self.lastScaleArchived = None
        self.lastPrice = self.lastCheckpoint
        print(self.__dict__)
    
    @property
    def marketData(self):
        return self.interface.marketData
    
    @property
    def data(self):
        data = {
            "positionSide":self.positionSide,
            "offset":str(self.offset),
            "rootCheckpoint":str(self.rootCheckpoint),
            "lastCheckpoint":str(self.lastCheckpoint)
        }
        return json.dumps(data)
    @property
    def previousCheckpoint(self):
        return self._getPreviousCheckpointPrice(self.lastCheckpoint)
    @property
    def nextCheckpoint(self):
        return self._getFollowingCheckpointPrice(self.lastCheckpoint)
    
    
    @property
    def pending_operations(self):
        return self.interface.get_pending_operations()
    
    def _getFollowingCheckpointPrice(self,checkpointPrice: Decimal):
        return checkpointPrice * self.offset

    def _getPreviousCheckpointPrice(self,checkpointPrice: Decimal):
        return checkpointPrice / self.offset
    def save(self):
        self.interface.saveStrategyState(self.data)
        
    def updatePriceCheckpoints(self,escalas:int):
        self.lastCheckpoint*=self.offset**escalas
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
    
    async def evaluar_precio(self, receivedPrice:Decimal):
        escalasSobrepasadas = self.calcular_saltos_en_progresion(self.lastCheckpoint, receivedPrice)
        if escalasSobrepasadas:
            print("\n","#"*4,f"evaluar_precio starts (receivedPrice '{receivedPrice}')",f"(previous:{self.previousCheckpoint}), (currentCheckpoint:{self.lastCheckpoint}), (following:{self.nextCheckpoint})","#"*4)

            print(f"{escalasSobrepasadas} escalas sobrepasadas con respecto a la ultima actualizacion")
        
            if receivedPrice >= self.nextCheckpoint:
                print(f"current_price >= self.nextCheckpoint")
                self.consecutives_price_fordward += 1
                
                if self.consecutives_price_fordward >= 2:
                    print("consecutives_price_fordward >= 2")
                    order = await self.interface.putOrder(self.positionSide, self.openingOrderSide, Decimal(self.get_min_amount(self.getMakerPrice(receivedPrice))), self.getMakerPrice(receivedPrice), "limit")
                    print(f"orden id:{order["info"]["clientOrderId"]}")
                    #pending_profit_operation = self.interface.create_pending_operations(order["id"],order["amount"],order["info"]["positionSide"], float(order["price"]), order["fee"],self.getProfitPriceOf(Decimal(str(order["price"]))))
                
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
                    print("·",end="",flush=True)
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

