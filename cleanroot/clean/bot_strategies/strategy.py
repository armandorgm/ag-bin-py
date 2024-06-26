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
    def saveState(self):
        pass
    
    @abstractmethod
    def evaluar_precio(self, datos_mercado:Decimal)->Any:
        pass
    
    @staticmethod
    def from_json(json_string:str):
        print("Strategy.from_json:")
        datos = json.loads(json_string)
        pprint(datos)
        return datos
    
    
    def get_min_amount(self,price:Decimal)->Decimal:
        rawAmount = (self.interface.notionalMin/price)
        print("rawAmount",rawAmount)
        print(self.interface.amountPrecision)
        formatedAmount = rawAmount.quantize(Decimal("1e-{0}".format(self.interface.amountPrecision)),rounding=ROUND_UP)
        print("formatedAmount",formatedAmount)
        return formatedAmount
    