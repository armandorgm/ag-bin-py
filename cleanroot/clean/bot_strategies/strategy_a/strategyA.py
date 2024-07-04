"""**********README
variables required
lastScale from initial price, permanentStore
"""
import asyncio
from decimal import ROUND_UP, Decimal,InvalidOperation
import simplejson as json
import math
from typing import Any, Callable, Literal, Optional, TypedDict

from ...interfaces.types import Ticker

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
        self.lastCheckpoint = Decimal(data["lastCheckpoint"]).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
        self.lastPrice = Decimal(data["lastCheckpoint"])
        self._profitOperations = data["profit_operations"]
        self.lastScaleArchived = None
        self.consecutives_price_fordward = data.get("consecutives_price_fordward",0)
        self.isJustLoaded = True
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
    
    #checkOpeningOrders was interfaz method
    async def checkOpeningOrders(self):
        print(f"checking Opening Orders (long/short) if executed/closed")
        closedOrders = []
        stillOpenOrders = []
        for origClientOrderId in self.openOrders:

                self.exchange.verbose = True
                orderData:Order = await self.exchange.fetch_order(origClientOrderId, self.symbol,{"origClientOrderId":origClientOrderId})
                self.exchange.verbose = False
                print(orderData["status"])
                if orderData["status"] == "closed": #before pending_profit_operation.check_price(current_price)
                    await self.strategy.onOpenOrderExecution(orderData)
                        
                else:#si la condicion no se cumple guardar la operacion
                    stillOpenOrders.append(origClientOrderId)
                    print(f"Precio de cierre de operacion NO alcanzado ({orderData["price"]})")
        self.openOrders = stillOpenOrders
    
    async def processPendingProfitOperations(self):
        pendingProfitOperations = []
        closedProfitOperations = [] 
        
        for po in self._profitOperations:
            opening = await self.interface.fetch_order(po["openingOrderId"])
            if opening and opening["status"] == "open":#case1 opening open
                pendingProfitOperations.append(po)
            elif opening and opening["status"] == "closed" and not po["closingOrderId"]:#case2 opening closed and closing None
                await self.onOpenOrderExecution(opening)
            elif po["closingOrderId"]:#case3 opening closed and closing not None 
                closing = await self.interface.fetch_order(po["closingOrderId"])
                if closing and closing["status"] == "open":#case3A opening closed and closing open
                    pendingProfitOperations.append(po)
                else: #case3B all closed
                    closedProfitOperations.append(po)
        self._profitOperations = pendingProfitOperations
        print(end="pendingProfitOp")
        pprint(pendingProfitOperations)
        print(end="closedProfitOp removed")
        pprint(closedProfitOperations)
                
                    

        
    async def preStart(self,ticker:Ticker):
        await self.processPendingProfitOperations()
        
    def _getFollowingCheckpointPrice(self,checkpointPrice: Decimal):
        return self.positionCalc(checkpointPrice, self.offset).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
        #old working just for "long" below:
            #return (checkpointPrice * self.offset).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))

    def _getPreviousCheckpointPrice(self,checkpointPrice: Decimal):
        return self.positionCalc(checkpointPrice, self.offset,True).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
        #old working just for "long" below:
            #return (checkpointPrice / self.offset).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
    
    def save(self):
        self.interface.saveStrategyState(self.cacheData)
        
    def updateLastCheckpoint(self,escalas:int):
        print(f"old lastCheckpoint == '{self.lastCheckpoint}'")
        #self.lastCheckpoint= (self.lastCheckpoint*(self.offset**escalas)).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
        self.lastCheckpoint= self.positionCalc(self.lastCheckpoint,(self.offset**escalas))
        print(f"new lastCheckpoint == '{self.lastCheckpoint}'")
        print(f"se actualizaron  escalas en un:+/-{escalas} currentCheckpoint:{self.lastCheckpoint}") 
    
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
        return result if self.positionSide.lower() == "long" else -result

    
    def getNthProgresionValueFromCheckpoint(self,numero_de_saltos_de_la_progresion:int,fromCheckpointPrice:Decimal):
        #value = fromCheckpointPrice * (self.offset**(numero_de_saltos_de_la_progresion))
        value = self.positionCalc(fromCheckpointPrice , (self.offset**(numero_de_saltos_de_la_progresion)))
        return value.quantize(Decimal("1e-{}".format(self.interface.pricePrecision)))
    
    def getProfitPriceOf(self, openPrice:Decimal):
        #return openPrice*self.offset # not good for Shorts ops
        return self.positionCalc(openPrice,self.offset)
    
    @property
    def openingOrderSide(self):
        return "buy" if self.positionSide.lower() == "long" else "sell"
    @property
    def closingOrderSide(self):
        return "sell" if self.positionSide.lower() == "long" else "buy"

    def parsePriceToDecimal(self,abstractNumber:str|int|float|Decimal)->Decimal:
        return Decimal(str(abstractNumber)).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
        
    async def isCheckpointProfitOperationActive(self, reachedCheckpoint:Decimal):
        print(f"Looking for {reachedCheckpoint} in ProfitOperation")
        for profit_Operation in self._profitOperations:
            #if type(profit_Operation["checkpoint"]) != type(checkpoint):
            #    raise TypeError(f"{type(profit_Operation["checkpoint"])}!={type(checkpoint)}{profit_Operation["checkpoint"]}!={checkpoint}")
            stored_N_Checkpoint =    self.parsePriceToDecimal(profit_Operation["checkpoint"])
            reachedCheckpointParsed= self.parsePriceToDecimal(reachedCheckpoint)
            #.quantize(Decimal("1e-{0}".format(self.interface.amountPrecision)),rounding=ROUND_UP)
            print(f"if {stored_N_Checkpoint} == {reachedCheckpointParsed} ({stored_N_Checkpoint==reachedCheckpointParsed})")
            if stored_N_Checkpoint == reachedCheckpointParsed:
                print(f"Found {reachedCheckpoint} in ProfitOperation")
                openingOrder = await self.interface.fetch_order(profit_Operation["openingOrderId"])
                if openingOrder:
                    if openingOrder["status"] == "open":
                        print(f"Opening order is ACTIVE (status:{openingOrder["status"]})")
                        return True
                    elif profit_Operation["closingOrderId"]:
                        print(f"Opening order for 'Checkpoint:{profit_Operation['checkpoint']}' is not open (current:{openingOrder["status"]})")
                        closingOrder = (await self.interface.fetch_order(profit_Operation["closingOrderId"]))
                        if closingOrder and closingOrder["status"] == "open":
                            print(f"Closing order is ACTIVE (status:{closingOrder["status"]})")
                            return True
            else:
                print(f"checkpoint {reachedCheckpoint} not found in storage {[op['checkpoint'] for op in self._profitOperations]}.by:StrategyA.isCheckpointProfitOperationActive")
        return False
    
    def updateProfitOperation(self,newProfitOperation:ProfitOperation):
        indice = next((i for i, po in enumerate(self._profitOperations) if po.get("checkpoint") == self.nextCheckpoint),None)
        if indice is not None:
            print("indice encontrado:",end="")
            pprint(self._profitOperations[indice])
            self._profitOperations[indice] = newProfitOperation
            print("operacion modificada:",end="")
            pprint(self._profitOperations[indice])
            print("all ProfitOperations:",end="")
            pprint(self._profitOperations)
        else:
            print("indice NO encontrado")
            self._profitOperations.append(newProfitOperation)
            print("operacion agregada",end=":")
            pprint(self._profitOperations)
        
    async def evaluar_precio(self, receivedPrice:Decimal):
        
        escalasSobrepasadas = self.calcular_saltos_en_progresion(self.lastCheckpoint, receivedPrice)
        if escalasSobrepasadas:
            print(f"\n{'#'*4} evaluar_precio starts{'#'*4} \nreceivedPrice '{receivedPrice}' {'· '*3}previous:{self.previousCheckpoint} {'· '*3}currentCheckpoint:{self.lastCheckpoint} {'· '*3}following:{self.nextCheckpoint}")

            print(f"Posiciones cambiadas ({escalasSobrepasadas})  con respecto a la ultima actualizacion")
        
            #if receivedPrice >= self.nextCheckpoint:
            if self.isNextCheckpointReached(receivedPrice):
                print(f"current_price (ALCANZÓ) self.nextCheckpoint")
                if self.consecutives_price_fordward >= 1:
                    if not (await self.isCheckpointProfitOperationActive(self.nextCheckpoint)) :
                        print(f"consecutives_price_fordward >= 2 ({self.consecutives_price_fordward >= 2})")
                        makerPrice = self.getMakerPrice(receivedPrice)
                        print(f"makerPrice is:{makerPrice}")
                        order = await self.interface.putOrder(self.positionSide, self.openingOrderSide, Decimal(self.get_min_amount(makerPrice)), makerPrice, "limit")
                        if order:
                            profitOperation:ProfitOperation = {"checkpoint":str(self.nextCheckpoint),"openingOrderId":order["info"]["clientOrderId"],"closingOrderId":None}
                            self.updateProfitOperation(profitOperation)
                            print(f"orden colocada con id:{order["info"]["clientOrderId"]}")
                            #pending_profit_operation = self.interface.create_pending_operations(order["id"],order["amount"],order["info"]["positionSide"], float(order["price"]), order["fee"],self.getProfitPriceOf(Decimal(str(order["price"]))))
                        else:
                            return
                    else:
                        print("self.isCheckpointProfitOperationActive == True")
                else:
                    print(f"self.consecutives_price_fordward is >= 2 ({self.consecutives_price_fordward >= 2})")
                self.consecutives_price_fordward += 1
                print(f"avances consecutivos actualizado (new:{self.consecutives_price_fordward})")
                self.updateLastCheckpoint (escalasSobrepasadas)
                
                                
            #elif receivedPrice <=self.previousCheckpoint:
            elif self.isNextCheckpointReached(receivedPrice,True):
                self.consecutives_price_fordward = 0
                self.updateLastCheckpoint (escalasSobrepasadas)
            
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
        #tick = 1/(Decimal("10")**self.interface.pricePrecision)
        tick = Decimal("1e-{0}".format(self.interface.pricePrecision))
        print(f"tick in getMakerPrice is: {tick}")
        if tick > currentPrice:
            raise ValueError(f"tick({tick}) cant be greater than price({currentPrice}). in Method StrategyA.getMakerPrice()")
        #print("tick=",tick)
        value = None
        if self.positionSide.lower() == "long":
            value = currentPrice+(tick*(-1))
        elif self.positionSide.lower() == "short":
            value = currentPrice+(tick)
        else:
            raise BaseException("Position Side Unknown")
        if value <= 0:
            raise ValueError(f"getMakerPrice is {value}")
        return value

    def getProfitOperationByOpenOrderId(self,clientOpenOrderId:str)->Optional[ProfitOperation]:
        for profit_operation in self._profitOperations:
            if profit_operation["openingOrderId"] == clientOpenOrderId:
                return profit_operation
    def getProfitOperationByCloseOrderId(self,clientCloseOrderId:str)->Optional[ProfitOperation]:
        for profit_operation in self._profitOperations:
            if profit_operation["closingOrderId"] == clientCloseOrderId:
                return profit_operation
        
    async def onOpenOrderExecution(self, openOrderData: Order):
        pprint(openOrderData)
        if openOrderData["amount"] and openOrderData["clientOrderId"]:
            closeOrder = await self.interface.putOrder(openOrderData["info"]["positionSide"],self.closingOrderSide,Decimal(openOrderData["amount"]), self.getProfitPriceOf(Decimal(str(openOrderData["price"]))), "limit")
            profit_operation = self.getProfitOperationByOpenOrderId(openOrderData["clientOrderId"])
            if profit_operation:
                profit_operation["closingOrderId"] = closeOrder["clientOrderId"]
            else:
                print(f"WARNING: opening order {openOrderData['clientOrderId']} not found in (profit_operation list) to add closing id")

    async def onCloseOrderExecution(self, closeOrderData: Order) -> None:
        print("close Order Executed")
        pprint(closeOrderData)
        if closeOrderData["amount"] and closeOrderData["clientOrderId"]:
            profit_operation = self.getProfitOperationByCloseOrderId(closeOrderData["clientOrderId"])
            if profit_operation:
                open_order = await self.interface.putOrder(closeOrderData["info"]["positionSide"],self.openingOrderSide, Decimal(closeOrderData["amount"]), profit_operation["checkpoint"], "limit")
                if open_order["clientOrderId"]:
                    profit_operation["closingOrderId"] = None
                    profit_operation["openingOrderId"] = open_order["clientOrderId"]
                else:
                    print(f"WARNING: couldnt update/reset (profit_operation list) with new opening order")
            else:
                print(f"WARNING: closing order {closeOrderData['clientOrderId']} not found in (profit_operation list) to update it")

    def positionCalc(self, priceCheckpoint:Decimal, offset:Decimal,reverse:bool=False)->Decimal:
        calc =[lambda x,y:x*y,lambda x,y:x/y]
        index:Optional[bool]=None
        if self.positionSide.lower() == "long":
            index = bool(0)
        elif self.positionSide.lower() == "short":
            index = bool(1)
        else:
            raise ValueError(f"Modo no válido {self.positionCalc}. Modos validos (long/short)")
        if reverse:
            index = not index
        if index == True and offset== 0:
            raise ZeroDivisionError
        return calc[index](priceCheckpoint,offset).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
    
    def isNextCheckpointReached(self,receivedPrice:Decimal,backwards:bool=False):
        calc =[
            lambda receivedPrice: receivedPrice >= self.nextCheckpoint,
            lambda receivedPrice: receivedPrice <= self.nextCheckpoint
            ]
        index:Optional[bool]=None
        if self.positionSide.lower() == "long":
            index = bool(0)
        elif self.positionSide.lower() == "short":
            index = bool(1)
        else:
            raise ValueError(f"Modo no válido {self.positionCalc}. Modos validos (long/short)")
        if backwards:
            index = not index
        return calc[index](receivedPrice)
        
    def onOrderUpdate(self,):
        pass
