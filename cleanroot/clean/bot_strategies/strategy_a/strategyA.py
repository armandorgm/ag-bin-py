from decimal import Decimal
import json
import math
from typing import Literal

from .types import CheckpointReachMessage
from ...interfaces.strategyA_dao_interface import iStrategyA_DAO

from ...interfaces.exchange_basic import PositionSide, SymbolPrecision
from ..profit_operation import Profit_Operation
from ..strategy import Strategy
from pprint import pprint
from...interfaces.exchange_basic import iStrategy_Callback_Signal
#getcontext().prec = 8

class StrategyA(Strategy):
    
    def __init__(self,precision:SymbolPrecision, offset:int|str|Decimal,initialPrice:int|str|Decimal,dao:iStrategyA_DAO) -> None:
        print(f"instancing StrategyA the offset argument=={offset}")
        self.symbolPrecision = precision
        self.offset = Decimal(str(offset))
        self.dao = dao
        self.consecutives_price_up = 0
        self.consecutives_price_down = 0
        self.active :bool = False
        self.pending_close_profit_operation_list = self.pending_operations
        self.positionSide:PositionSide="long"
        self._ref_price = initialPrice
        self.previousPrice = self.getPreviousCheckpointPrice(Decimal(initialPrice))
        self.nextPrice = self.getFollowingCheckpointPrice(Decimal(initialPrice))
    
    
    @property
    def pending_operations(self):
        return self.dao.get_pending_operations()
    
    def getFollowingCheckpointPrice(self,price: Decimal):
        return price * (1+self.offset)

    def getPreviousCheckpointPrice(self,price: Decimal):
        return price / (1+self.offset)
                    
    @property
    def reference_price(self):
        return self._ref_price

    def updatePriceCheckpoints(self,new_ref_price:Decimal, checkpointReached:CheckpointReachMessage): 
        if(checkpointReached =="price_moved_up"):
            pass
        elif checkpointReached == "price_moved_down":
            pass
        else:
            raise BaseException(f"CheckpointReachMessage Unhandled {checkpointReached}")

        

    @property
    def amount(self):
        return self.get_min_amount()
    
    def get_min_amount(self):
       return 43
    
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
        
    def updateConsecutiveMovements(self, precio_actual, orden_callback, price_movement:Literal["price_moved_up","price_moved_down"])->int:
        """
        updates and get the numbers of checkpoint surpassed
        """
        
        print("#"*10,f"precio {"superior" if price_movement == "price_moved_up" else "inferior"} alcanzado","#"*10)
        self.consecutives_price_up = self.consecutives_price_up + 1 if price_movement == "price_moved_up" else 0
        self.consecutives_price_down = self.consecutives_price_down + 1 if price_movement == "price_moved_down" else 0

    def getProfitPriceOf(self, openPrice:Decimal):
        return openPrice*(1+self.offset)
    
    def evaluar_precio(self, current_price:Decimal, orden_callback: iStrategy_Callback_Signal):
        operaciones_restantes = []
        self.currentPrice = current_price
        if current_price >= self.nextPrice:
            priceMovement = "price_moved_up"
            self.updateConsecutiveMovements(current_price, orden_callback, priceMovement)
            self.updatePriceCheckpoints (current_price,priceMovement)
            if self.consecutives_price_up >= 2:
                order = orden_callback("LONG", "BUY", Decimal(self.amount), current_price)
                print(order)
                print("preIntance close_trigger",self.nextPrice,type(self.nextPrice))
                if order["id"]:
                    pending_profit_operation = self.dao.create_pending_operations(order["id"],order["amount"],order["info"]["positionSide"], order["average"], json.dumps(order["fee"]),self.nextPrice)
                self.pending_close_profit_operation_list.append(pending_profit_operation)

        elif current_price <=self.previousPrice:
            print("#"*10,"precio inferior alcanzado","#"*10)
            self.consecutives_price_up = 0
            self.reference_price = current_price
            if self.consecutives_price_down >= 2:
                order = orden_callback("SHORT", "SELL", self.amount, current_price)
                print(order)
                pending_profit_operation = Profit_Operation(current_price,"SHORT", self.previousPrice, self.amount)
                self.pending_close_profit_operation_list.append(pending_profit_operation)
        else:
            print("price no changed")


        #Revisar si hay ordenes por cerrar
        print("Ordenes pendientes por cerrar:", len(self.pending_close_profit_operation_list))
        for pending_profit_operation in self.pending_close_profit_operation_list:
            if pending_profit_operation.check_price(current_price):
                print("Precio de cierre de operacion alcanzado")
                order_side = "sell" if self.positionSide.lower() == "LONG" else "buy"
                orden_callback(pending_profit_operation.position_side, order_side, pending_profit_operation.amount,pending_profit_operation.close_price)
            else:
                print("Precio de cierre de operacion NO alcanzado")
                operaciones_restantes.append(pending_profit_operation)
                
        self.pending_close_profit_operation_list = operaciones_restantes
            
        #if(datos_mercado["precio_actual"]>)
        print("la estrategia debe evaluar aqui que hacer")
        pprint(current_price)
        print("precio de referencia:",self.reference_price, "lowerPrice",self.previousPrice,"upperPrice",self.nextPrice)
        return None, None
    
