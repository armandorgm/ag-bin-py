"""**********README
variables required
lastScale from initial price, permanentStore
"""
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
    
    def __init__(self, interface:StrategyImplementor, positionSide:PositionSide, offset:int|str|Decimal,initialReferenceCheckpoint:int|str|Decimal) -> None:
        super().__init__(interface)
        self.offset = Decimal(str(offset))
        self.consecutives_price_fordward = 0
        self.positionSide = positionSide
        self.bornPrice = Decimal(str(initialReferenceCheckpoint))
        self.reference_price = self.bornPrice
    
    @property
    def marketData(self):
        return self.interface.marketData
    
    def saveState(self):
        self.interface.saveStrategyState(json.dumps(self.__dict__))
    @property
    def previousPrice(self):
        return self.getPreviousCheckpointPrice(self.reference_price)
    @property
    def nextPrice(self):
        return self.getFollowingCheckpointPrice(self.reference_price)
    
    
    @property
    def pending_operations(self):
        return self.interface.get_pending_operations()
    
    def getFollowingCheckpointPrice(self,price: Decimal):
        return price * (1+self.offset)

    def getPreviousCheckpointPrice(self,price: Decimal):
        return price / (1+self.offset)
                    


    def updatePriceCheckpoints(self,escalas:int):
        print("antes:",self.reference_price,f"type:{type(self.reference_price)}")
        self.reference_price*=(1+self.offset)**escalas
        print("despues:",self.reference_price,f"type:{type(self.reference_price)}")
        print(f"se actualizaron  escalas en un:{escalas} ahora:{self.reference_price}") 
        
    
    def calcular_saltos_en_progresion(self, valor_inicial:Decimal, valor_final:Decimal):
        mathOffset:Decimal = 1+self.offset
        x = valor_final/valor_inicial
        if(x>0):
            rawResult = math.log(abs(x), mathOffset)
            result = int(rawResult)
            return result
        else:
            return 99
 

    def getProfitPriceOf(self, openPrice:Decimal):
        return openPrice*(1+self.offset)
    
    @property
    def openingOrderSide(self):
        return "buy" if self.positionSide.lower() == "long" else "sell"
    @property
    def closingOrderSide(self):
        return "sell" if self.positionSide.lower() == "long" else "buy"
    
    async def evaluar_precio(self, current_price:Decimal):
        print("#"*4,f"evaluar_precio starts at '{current_price}'","#"*4)
        
        escalasSobrepasadas = self.calcular_saltos_en_progresion(self.reference_price, current_price)
        print(f"{escalasSobrepasadas} escalas sobrepasadas con respecto a la ultima actualizacion")
        
        if escalasSobrepasadas:
            if current_price >= self.nextPrice:
                self.consecutives_price_fordward += 1
                self.updatePriceCheckpoints (escalasSobrepasadas)
                
                if self.consecutives_price_fordward >= 2:
                    order = self.interface.putOrder(self.positionSide, self.openingOrderSide, Decimal(self.get_min_amount(self.getMakerPrice(current_price))), self.getMakerPrice(current_price), "limit")
                    #pending_profit_operation = self.interface.create_pending_operations(order["id"],order["amount"],order["info"]["positionSide"], float(order["price"]), order["fee"],self.getProfitPriceOf(Decimal(str(order["price"]))))
                                
            elif current_price <=self.previousPrice:
                self.consecutives_price_fordward = 0
                self.updatePriceCheckpoints (escalasSobrepasadas)

        else:
            print("checkpoint not reached ")
        
    def getMakerPrice(self,currentPrice:Decimal):
        tick = 1/(Decimal(10)**self.interface.pricePrecision)
        if tick > currentPrice:
            raise ValueError(f"tick({tick}) cant be greater than price({currentPrice}). in Method StrategyA.getMakerPrice()")
        print("tick=",tick)
        if self.positionSide.lower() == "long":
            return currentPrice+(tick*(-1))
        elif self.positionSide.lower() == "short":
            return currentPrice+(tick)
        else:
            raise BaseException("Position Side Unknown")