
import math
from bot_strategies.strategy import Strategy
from pprint import pprint

class StrategyA(Strategy):
    def __init__(self,offset) -> None:
        super().__init__(offset)
        self._ref_price = None
        self.lower_price = None
        self.upper_price = None
        self.consecutives_price_up = 0
        self.consecutives_price_down = 0
        self.position_mode = None
    
    @property
    def ref_price(self):
        return self._ref_price
    @ref_price.setter
    def ref_price(self,new_ref_price):
        self._ref_price = new_ref_price
        self.upper_price = new_ref_price * (1+(self.offset/100))
        self.lower_price = new_ref_price * (1-(self.offset/100))
        
    def evaluar_orden(self, datos_mercado):
        if not self.ref_price:
            self.ref_price = datos_mercado["precio_actual"]
            
        elif datos_mercado["precio_actual"] >=self.upper_price:
            print("#"*10,"precio superior alcanzado","#"*10)
            self.consecutives_price_up = self.consecutives_price_up + 1
            self.consecutives_price_down = 0
            self.ref_price = datos_mercado["precio_actual"]
            if self.consecutives_price_up >= 2:
                self.position_mode = "LONG"
            self.backSignal("")
            
        elif datos_mercado["precio_actual"] <=self.lower_price:
            print("#"*10,"precio inferior alcanzado","#"*10)
            self.consecutives_price_down = self.consecutives_price_down + 1
            self.consecutives_price_up = 0
            self.ref_price = datos_mercado["precio_actual"]
        
            
        #if(datos_mercado["precio_actual"]>)
        print("la estrategia debe evaluar aqui que hacer")
        pprint(datos_mercado)
        print("precio de referencia:",self.ref_price, "lowerPrice",self.lower_price,"upperPrice",self.upper_price)
        return None, None
    
