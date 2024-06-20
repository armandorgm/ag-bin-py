from decimal import ROUND_UP, Decimal
import math
from typing import Literal
from .types import CheckpointReachMessage
from ...interfaces.strategyA_dao_interface import iStrategyA_DAO
from ..profit_operation import Profit_Operation
from ..strategy import Strategy
from pprint import pprint
import ccxt
from...interfaces.exchange_basic import iStrategy_Callback_Signal,MarketInterface,PositionSide, SymbolPrecision
#getcontext().prec = 8

class StrategyA(Strategy):
    
    
    def __init__(self,marketData:MarketInterface, offset:int|str|Decimal,currentCheckpoint:int|str|Decimal,dao:iStrategyA_DAO) -> None:
        self.marketData = marketData
        pprint(marketData["info"]["filters"][5])
        self.offset = Decimal(str(offset))
        self.dao = dao
        self.consecutives_price_up = 0
        self.consecutives_price_down = 0
        self.active :bool = False
        self.pending_close_profit_operation_list = self.pending_operations
        self.positionSide:PositionSide="long"
        self.reference_price = Decimal(str(currentCheckpoint))
        self.createOrder: iStrategy_Callback_Signal|None = None

    @property
    def previousPrice(self):
        return self.getPreviousCheckpointPrice(self.reference_price)
    @property
    def nextPrice(self):
        return self.getFollowingCheckpointPrice(self.reference_price)
    
    
    @property
    def pending_operations(self):
        return self.dao.get_pending_operations()
    
    def getFollowingCheckpointPrice(self,price: Decimal):
        return price * (1+self.offset)

    def getPreviousCheckpointPrice(self,price: Decimal):
        return price / (1+self.offset)
                    


    def updatePriceCheckpoints(self,escalas:int):
        print("antes:",self.reference_price,f"type:{type(self.reference_price)}")
        self.reference_price*=(1+self.offset)**escalas
        print("despues:",self.reference_price,f"type:{type(self.reference_price)}")
        print(f"se actualizaron  escalas en un:{escalas} ahora:{self.reference_price}") 
        

    @property
    def amount(self):
        return self.get_min_amount()
    
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
        return self.marketData["precision"]["price"]

    def get_min_amount(self,price:Decimal|None=None):
        if not price:
            price = self.currentPrice
        rawAmount = (self.notionalMin/price)
        print("rawAmount",rawAmount)
        formatedAmount = rawAmount.quantize(Decimal("1e-{0}".format(self.amountPrecision)),rounding=ROUND_UP)
        print("formatedAmount",formatedAmount)
        return formatedAmount
    
    def calcular_saltos_en_progresion(self, valor_inicial:Decimal, valor_final:Decimal):
        mathOffset:Decimal = 1+self.offset
        return int(math.log(valor_final/valor_inicial, mathOffset))

         
    def getNextGeometricBound(self,progresionCheckpoint:Decimal,currentPrice:Decimal):
        """
        Obtiene el valor de la progresion proximo a otro valor
        """
        if self.offset <=0:
            raise BaseException(f"offset({self.offset}) would cause infinite recursion")
        if progresionCheckpoint < currentPrice:
            newCheckpoint = self.getFollowingCheckpointPrice(progresionCheckpoint)
            if newCheckpoint > currentPrice:
                return newCheckpoint
            else:
                return self.getNextGeometricBound(newCheckpoint,currentPrice)
        elif progresionCheckpoint > currentPrice:
            newCheckpoint = self.getPreviousCheckpointPrice(progresionCheckpoint)
            if newCheckpoint < currentPrice:
                return progresionCheckpoint
            else:
                return self.getNextGeometricBound(newCheckpoint,currentPrice)
        else:
            return self.getFollowingCheckpointPrice(progresionCheckpoint) 
        
    def getProfitPriceOf(self, openPrice:Decimal):
        return openPrice*(1+self.offset)
    
    async def checkPendingOrdersToClose(self,current_price:Decimal):
            """
            Revisar si hay ordenes por cerrar
            """
            operaciones_restantes = []
            print("Ordenes pendientes por cerrar:", len(self.pending_close_profit_operation_list))
            for pending_profit_operation in self.pending_close_profit_operation_list:
                pprint(pending_profit_operation)
                if pending_profit_operation.check_price(current_price):
                    print(f"Precio de cierre de operacion alcanzado ({pending_profit_operation.close_price})")
                    order_side = "sell"
                    try:
                        order = await self.createOrder(pending_profit_operation.position_side, order_side, pending_profit_operation.amount,pending_profit_operation.close_price,"limit") # type: ignore
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
                    operaciones_restantes.append(pending_profit_operation)
                    
            self.pending_close_profit_operation_list = operaciones_restantes
    
    async def evaluar_precio(self, current_price:Decimal, createOrder: iStrategy_Callback_Signal):
        print("#"*20,f"evaluar_precio starts at '{current_price}'","#"*20)
        self.createOrder = createOrder
        self.currentPrice = current_price
        #Revisar si hay ordenes por cerrar
        await self.checkPendingOrdersToClose(current_price)
        
        if current_price >= self.nextPrice:
            escalasSobrepasadas = self.calcular_saltos_en_progresion(self.reference_price, current_price)
            print(f"{escalasSobrepasadas} escalas sobrepasadas con respecto a la ultima actualizacion")
            self.consecutives_price_up += escalasSobrepasadas

            self.updatePriceCheckpoints (escalasSobrepasadas)
            if self.consecutives_price_up >= 2:
                order = await createOrder("LONG", "BUY", Decimal(self.amount), current_price,"market")
                if not order["average"]:
                    pprint(order)
                print("preIntance close_trigger",self.nextPrice,type(self.nextPrice))
                if order["id"] and order["price"]:
                    pending_profit_operation = self.dao.create_pending_operations(order["id"],order["amount"],order["info"]["positionSide"], float(order["price"]), order["fee"],self.getProfitPriceOf(Decimal(str(order["price"]))))
                self.pending_close_profit_operation_list.append(pending_profit_operation)

        elif current_price <=self.previousPrice:
            print("#"*10,"precio inferior alcanzado","#"*10)
            escalasSobrepasadas = self.calcular_saltos_en_progresion(self.reference_price, current_price)
            print(f"{escalasSobrepasadas} escalas sobrepasadas con respecto a la ultima actualizacion")
            self.updatePriceCheckpoints (escalasSobrepasadas)

            self.consecutives_price_up = 0
        else:
            print("checkpoint not reached ")


        
            
        print("#"*20,f"evaluar_precio ends prev:{self.previousPrice.quantize(Decimal("1e-{0}".format(self.pricePrecision)))} actual:{self.reference_price.quantize(Decimal("1e-{0}".format(self.pricePrecision)))} next:{self.nextPrice.quantize(Decimal("1e-{0}".format(self.pricePrecision)))}","#"*20)
        return None, None
    
