
from typing import Callable, List, Literal
from ..profit_operation import Profit_Operation
from ..strategy import Strategy
from pprint import pprint
from .strategyA_dao import StrategyA_DAO

class StrategyA(Strategy):
    def __init__(self,id:int, offset) -> None:
        super().__init__(offset)
        self.id = id
        self.dao = StrategyA_DAO(self.__class__.__name__+".db")
        self._ref_price = None
        self.lower_price = None
        self.upper_price = None
        self.consecutives_price_up = 0
        self.consecutives_price_down = 0
        self.position_side :bool= None
        self.pending_close_profit_operation_list = self.pending_operations
    
    
    @property
    def pending_operations(self):
        return self.dao.get_pending_operations()
    
    @property
    def reference_price(self):
        return self.dao.get_reference_price(self.id)
    @reference_price.setter
    def reference_price(self,new_ref_price:float):
        self._ref_price = new_ref_price
        self.upper_price = new_ref_price * (1+(self.offset/100))
        self.lower_price = new_ref_price * (1-(self.offset/100))
    
    @property
    def amount(self):
        return self.get_min_amount()
    
    def get_min_amount(self):
       return 43
                
    
    def procesar_operacion(self, precio_actual, orden_callback, price_movement:Literal["price_moved_up","price_moved_down"]):
        print("#"*10,f"precio {"superior" if price_movement == "price_moved_up" else "inferior"} alcanzado","#"*10)
        self.consecutives_price_up = self.consecutives_price_up + 1 if price_movement == "price_moved_up" else 0
        self.consecutives_price_dow = self.consecutives_price_dow + 1 if price_movement == "price_moved_down" else 0

        if price_movement == "price_moved_up":
            self.consecutives_price_up = self.consecutives_price_up + 1

        else:
            print("#" * 10, f"precio {price_movement.lower()} alcanzado", "#" * 10)

    def evaluar_precio(self, datos_mercado, orden_callback: Callable[[str, float, int], None]):
        operaciones_restantes = []

        if self.reference_price:
            if datos_mercado["precio_actual"] >=self.upper_price:
                self.procesar_operacion(datos_mercado, orden_callback, "price_moved_up")

                print("#"*10,"precio superior alcanzado","#"*10)
                self.consecutives_price_up = self.consecutives_price_up + 1
                self.consecutives_price_down = 0
                self.reference_price = datos_mercado["precio_actual"]
                if self.consecutives_price_up >= 2:
                    self.position_side = "LONG"
                    order = orden_callback("LONG", "BUY", self.amount, datos_mercado["precio_actual"])
                    print(order)
                    print("preIntance close_trigger",self.upper_price,type(self.upper_price))
                    profit_operation = Profit_Operation(datos_mercado["precio_actual"],"LONG", self.upper_price,self.amount)
                    self.pending_close_profit_operation_list.append(profit_operation)

            elif datos_mercado["precio_actual"] <=self.lower_price:
                print("#"*10,"precio inferior alcanzado","#"*10)
                self.consecutives_price_down = self.consecutives_price_down + 1
                self.consecutives_price_up = 0
                self.reference_price = datos_mercado["precio_actual"]
                if self.consecutives_price_down >= 2:
                    self.position_side = "SHORT"
                    order = orden_callback("SHORT", "SELL", self.amount, datos_mercado["precio_actual"])
                    print(order)
                    profit_operation = Profit_Operation(datos_mercado["precio_actual"],"SHORT", self.lower_price, self.amount)
                    self.pending_close_profit_operation_list.append(profit_operation)
        else:
            self.reference_price = datos_mercado["precio_actual"]

        #Revisar si hay ordenes por cerrar
        print("Ordenes pendientes por cerrar:", len(self.pending_close_profit_operation_list))
        for op_raw in self.pending_close_profit_operation_list:
            op = Profit_Operation(op_raw.entry_price,op_raw.position_side,op_raw.closing_price, op_raw.amount)
            if op.check_price(datos_mercado["precio_actual"]):
                print("Precio de cierre de operacion alcanzado")
                order_side = "sell" if self.position_side.lower() == "LONG" else "buy"
                orden_callback(op.position_side, order_side, op.amount,op.close_price_trigger)
            else:
                print("Precio de cierre de operacion NO alcanzado")
                operaciones_restantes.append(op)
                
        self.pending_close_profit_operation_list = operaciones_restantes
            
        #if(datos_mercado["precio_actual"]>)
        print("la estrategia debe evaluar aqui que hacer")
        pprint(datos_mercado)
        print("precio de referencia:",self.reference_price, "lowerPrice",self.lower_price,"upperPrice",self.upper_price)
        return None, None
    
if __name__ == "main":
    dao = StrategyA_DAO("lala")