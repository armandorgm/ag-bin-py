"""**********README
variables required
lastScale from initial price, permanentStore
"""
import asyncio
from decimal import ROUND_UP, Decimal,InvalidOperation
from queue import Queue
import time
import simplejson as json
import math
from typing import Any, Callable, Dict, List, Literal, Optional, TypedDict, Union

from ...interfaces.types import Ticker

from ...interfaces.strategy_interface import StrategyImplementor
from ..profit_operation import Profit_Operation
from ..strategy import Strategy
from pprint import pprint
import ccxt
from...interfaces.exchange_basic import Order, iStrategy_Callback_Signal,MarketInterface,PositionSide, SymbolPrecision, ProfitOperation
from ccxt.base.errors import InvalidOrder, OrderNotFound
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
        self._onOrderUpdateQueue = Queue()
    
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
        print(f"There are {len(self._profitOperations)} pending operations")
        
        for po in self._profitOperations:
            if po["closingOrderId"]:
                try:
                    closing = await self.interface.fetch_order(po["closingOrderId"])
                except OrderNotFound as e:
                    print(f"ERROR: OUT order {po["closingOrderId"]} no existe. Posible razón: se reemplazó la orden de cierre ejecutada por otra duplicada por falta de seguridad en la actualizacíon de las operaciones. Solucion no recomandada para salir del paso:se eliminara la operacion")
                    self._profitOperations.remove(po)
                    print(f"operacion removida:",po,"\nReinicializando el procesamiento de las operaciones pendientes")
                    return await self.processPendingProfitOperations()
                if closing["status"] == "closed":
                    res = self.removePendingOperationBy("closingOrderId",po["closingOrderId"])
                    if res:
                        print(f"Checkpoint {res['checkpoint']} with OUT order status{closing["status"]}removed successfully. reinitializing preCheck...")
                        return await self.processPendingProfitOperations()
                elif closing["status"] != "open":
                    print(f"Desarrollo pendiente para operaciones con ordenes {closing["status"]} que no se pudieron cerrar po X motivos...")
            else: #if po["closingOrderId"] == None
                opening = await self.interface.fetch_order(po["openingOrderId"])
                if opening["status"] == "closed":
                    await self.onOpenOrderExecution(opening)
                elif opening["status"] != "open":
                    print(f"Desarrollo pendiente para operaciones con ordenes {opening["status"]} que no se pudieron cerrar po X motivos...")

        self.save()
        print(end="pendingProfitOp: ")
        
        
    async def preInit(self,ticker:Ticker):
        print("preInit() start "*4)
        await self.processPendingProfitOperations()
        print("preInit() ends "*4)

        
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
        print(f"lastCheckpoint changed from '{self.lastCheckpoint}'",end=" ")
        #self.lastCheckpoint= (self.lastCheckpoint*(self.offset**escalas)).quantize(Decimal("1e-{0}".format(self.interface.pricePrecision)))
        self.lastCheckpoint= self.positionCalc(self.lastCheckpoint,(self.offset**escalas))
        print(f">>> to '{self.lastCheckpoint}'")
    
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
        print(f"Looking for {reachedCheckpoint} in ProfitOperation",end=": ")
        reachedCheckpointFound = False
        for profit_Operation in self._profitOperations:
            #if type(profit_Operation["checkpoint"]) != type(checkpoint):
            #    raise TypeError(f"{type(profit_Operation["checkpoint"])}!={type(checkpoint)}{profit_Operation["checkpoint"]}!={checkpoint}")
            stored_N_Checkpoint =    self.parsePriceToDecimal(profit_Operation["checkpoint"])
            reachedCheckpointParsed= self.parsePriceToDecimal(reachedCheckpoint)
            if stored_N_Checkpoint == reachedCheckpointParsed:
                reachedCheckpointFound = True
                print(f"Found {reachedCheckpoint} in ProfitOperation")
                try:
                    openingOrder = await self.interface.fetch_order(profit_Operation["openingOrderId"])
                except Exception as e:
                    print("ERROR: fetching order para la verificacion si una operacion in/out sigue activa")
                    raise e
                if openingOrder:
                    print(f"fetched IN order correctly")
                    if openingOrder["status"] == "open":
                        print(f"Opening order is ACTIVE (status:{openingOrder["status"]})")
                        return True
                    else:
                        print(f"Opening order for 'Checkpoint:{profit_Operation['checkpoint']}' is not open (current:{openingOrder["status"]})")
                        if profit_Operation["closingOrderId"]:
                            closingOrder = (await self.interface.fetch_order(profit_Operation["closingOrderId"]))
                            if closingOrder and closingOrder["status"] == "open":
                                print(f"OUT order is 'open' (status:{closingOrder["status"]})")
                                return True
                            else:
                                print(f"OUT order is NOT 'open'")
                
        if not reachedCheckpointFound:  
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
        else:
            print("indice NO encontrado")
            self._profitOperations.append(newProfitOperation)
            print("operacion agregada",end=":")
            pprint(self._profitOperations)
            
    async def onNextCheckpointReached(self,receivedPrice:Decimal,escalasSobrepasadas:int):
        print(f"current_price (ALCANZÓ) self.nextCheckpoint")
        if self.consecutives_price_fordward >= 1:
            if not (await self.isCheckpointProfitOperationActive(self.nextCheckpoint)) :
                print(f"consecutives_price_fordward >= 1 ({self.consecutives_price_fordward >= 1})")
                newClientOrderId = self.interface.idUnico
                makerPrice = self.getMakerPrice(receivedPrice)
                amount = Decimal(self.get_min_amount(makerPrice))
                print(f"makerPrice is:{makerPrice}")
                profitOperation:ProfitOperation = {"checkpoint":str(self.nextCheckpoint),"openingOrderId":newClientOrderId,"closingOrderId":None}
                self.updateProfitOperation(profitOperation)
                print(f"IN orden registrada en pending Operations con id:{newClientOrderId}")
                #pending_profit_operation = self.interface.create_pending_operations(order["id"],order["amount"],order["info"]["positionSide"], float(order["price"]), order["fee"],self.getProfitPriceOf(Decimal(str(order["price"]))))
                order = await self.interface.putOrder(newClientOrderId,self.positionSide, self.openingOrderSide, amount, makerPrice, "limit")
                
                
            else:
                print("self.isCheckpointProfitOperationActive == True")
        else:
            print(f"self.consecutives_price_fordward is >= 1 ({self.consecutives_price_fordward >= 1})")
        self.consecutives_price_fordward += 1
        print(f"avances consecutivos actualizado (new:{self.consecutives_price_fordward})")
        self.updateLastCheckpoint (escalasSobrepasadas)
                        
    async def evaluar_precio(self, receivedPrice:Decimal):
        try:
            escalasSobrepasadas = self.calcular_saltos_en_progresion(self.lastCheckpoint, receivedPrice)
            if escalasSobrepasadas:
                print(f"\n{'#'*4} evaluar_precio starts{'#'*4} \nreceivedPrice '{receivedPrice}' {'· '*3}previous:{self.previousCheckpoint} {'· '*3}currentCheckpoint:{self.lastCheckpoint} {'· '*3}following:{self.nextCheckpoint}")
                print(f"Posiciones cambiadas ({escalasSobrepasadas})  con respecto a la ultima actualizacion")
            
                #if receivedPrice >= self.nextCheckpoint:
                if self.isNextCheckpointReached(receivedPrice):
                    await self.onNextCheckpointReached(receivedPrice,escalasSobrepasadas)       
                elif self.isNextCheckpointReached(receivedPrice,True):#if receivedPrice <=self.previousCheckpoint
                    self.consecutives_price_fordward = 0
                    self.updateLastCheckpoint (escalasSobrepasadas)
                    
                self.lastScaleArchived = escalasSobrepasadas
                self.save()

            else:#arrow printing if no checkpoint reach in second call
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
        except Exception as e:
            print(e)
            print("ERROR: Evaluando precio. Skiping...")
        

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
        
    async def onOpenOrderExecution(self, openingOrderData: Order):
        try:
            if openingOrderData["amount"] and openingOrderData["clientOrderId"]:
        
                positionSide = openingOrderData["info"]["positionSide"] if "positionSide" in openingOrderData["info"] else openingOrderData["info"]["ps"]
                newClientOrderId = self.interface.idUnico

                profit_operation = self.getProfitOperationByOpenOrderId(openingOrderData["clientOrderId"])
                if profit_operation:
                    profit_operation["closingOrderId"] = newClientOrderId
                    print(f"OUT orden registrada en pending Operations con id:{newClientOrderId}")
                    closeOrder = await self.interface.putOrder(newClientOrderId, positionSide,self.closingOrderSide,Decimal(openingOrderData["amount"]), self.getProfitPriceOf(Decimal(str(openingOrderData["average"]))), "limit")
                else:
                    print(f"WARNING: opening order {openingOrderData['clientOrderId']} not found in (profit_operation list) to add closing id")
                assert closeOrder is not None, "closeOrder should not be None"
        except InvalidOrder as e:
            print(e["code"])
            if e["code"] == -2022:
                pass
            print("#"*20,e,"#"*20)


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
    
    def is_an_opening_order_in_pending_operations(self, closedClientOrderId:str)->bool:
        for po in self._profitOperations:
            if po["openingOrderId"] == closedClientOrderId:
                return True
        return False
                
    async def onOrderUpdate(self,orderReceived:Order):
        self._onOrderUpdateQueue.put(orderReceived)
        while not self._onOrderUpdateQueue.empty():
            order = self._onOrderUpdateQueue.get()
            assert order["status"] is not None
            testIdList = ([po["openingOrderId"] for po in self._profitOperations]+[po2["closingOrderId"] for po2 in self._profitOperations if po2["closingOrderId"]])
            #print(f"prueba de codigo para obtener lista plana de todos los id de ordenes. cantidad de ops({len(self._profitOperations)}) cantidad de ids({len(testIdList)}):",)
            #pprint(testIdList)
            if order["clientOrderId"] in testIdList:
                #self.ownedOrderIds.remove(order["clientOrderId"])
                position_side = order["info"]["ps"].lower()
                order_side = order["side"]
                
                print("onOrderUpdate starts...")
                print(time.ctime(), order["clientOrderId"],order["symbol"],order["info"]["ps"],order["side"],order["status"],f"(amount={order["amount"]})",f"(filled={order["filled"]})",f"(remaining={order["remaining"]})")
                if position_side == "long" and order_side.lower() == "buy" or \
                position_side == "short" and order_side.lower() == "sell":
                    print("it's an 'IN  Op. order' ",end="| ")
                    if order["clientOrderId"] and self.is_an_opening_order_in_pending_operations(order["clientOrderId"]):
                        print("found in pending list",end=" | ")
                        if(order["status"].lower() == "closed"):
                            print("order closed | Action: Calling onOpenOrderExecution(Order)")
                            await self.onOpenOrderExecution(order)
                        else:
                            print(f"operation IN is not closed | actually({order["status"]})")
                    else:
                        print("not in operation list. Action: nothing...")
                else:
                    print("it's a 'OUT' order",end=" | ")
                    if order["status"] == "closed":
                        print("status(closed)", end=" | ")
                        if order["clientOrderId"] in [ po["closingOrderId"] for po in self._profitOperations]:
                            print("found in pending list",end=" | ")
                            print("Action(Delete it)",end=" >>> ")
                            res= self.removePendingOperationBy("closingOrderId",order["clientOrderId"])
                            print(("SUCCESS" if res else "FAIL")+f" deteling operation"+f"checkpoint({res["checkpoint"]})" if res else "")
                                
                print("onOrderUpdate ends...")
    
    def removePendingOperationBy(self,key:Literal["closingOrderId"],value:Any)->Optional[ProfitOperation]:
        for po in self._profitOperations:
            if po[key] == value:
                self._profitOperations.remove(po)
                return po
