from decimal import ROUND_UP, Decimal
import json
from pprint import pprint
from typing import Any, Awaitable, Callable, Coroutine, List
from abc import ABC, abstractmethod

from ..interfaces.strategy_interface import StrategyImplementor

from ..interfaces.types import OrderType
from ..interfaces.exchange_basic import SymbolPrecision,Order,PositionSide,OrderSide
class Strategy(ABC):
    """
    The Strategy interface declares operations common to all supported versions
    of some algorithm.

    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.
    """
    """
    @abstractmethod
    def do_algorithm(self, data: List):
        pass
    """
    def __init__(self,interface:StrategyImplementor) -> None:
        self.interface = interface
        
    @abstractmethod
    def data(self)->str:
        pass
    
    @abstractmethod
    async def onOpenOrderExecution(self,orderData:Order)->None:
        """
        Es el aviso que le brinda el bot a la estrategia cuando una orden "Open" tiene el status "closed
        """
        pass
    @abstractmethod
    async def onCloseOrderExecution(self,orderData:Order)->None:
        """
        Es el aviso que le brinda el bot a la estrategia cuando una orden "Close" tiene el status "closed
        """
        pass
    
    @abstractmethod
    def evaluar_precio(self, datos_mercado:Decimal)->Any:
        pass
    
    @staticmethod
    def save(self):
        pass
            
    @staticmethod
    def from_json(json_string:str):
        print("Strategy.from_json:")
        datos = json.loads(json_string)
        pprint(datos)
        return datos
    
    
    def get_min_amount(self,price:Decimal)->Decimal:
        """
        Entrega el monto minimo formateado en el que puede abrirse una orden para un simbolo en especifico y 
        formateado en la precision correcta para que sea valido para el exchange
        """
        rawAmount = (self.interface.notionalMin/price)
        formatedAmount = rawAmount.quantize(Decimal("1e-{0}".format(self.interface.amountPrecision)),rounding=ROUND_UP)
        return formatedAmount
    