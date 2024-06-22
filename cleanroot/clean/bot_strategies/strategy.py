from decimal import Decimal
from typing import Any, Awaitable, Callable, Coroutine, List
from abc import ABC, abstractmethod

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
    

    @abstractmethod
    def evaluar_precio(self, datos_mercado:Decimal, orden_callback: Callable[[PositionSide, OrderSide, Decimal, Decimal,OrderType], Coroutine[Any,Any,Order]])->Coroutine[Any,Any,Order]:
        pass