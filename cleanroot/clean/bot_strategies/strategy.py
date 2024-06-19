from decimal import Decimal
from typing import Callable, List
from abc import ABC, abstractmethod

from ..interfaces.exchange_basic import SymbolPrecision
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
    def evaluar_precio(self, datos_mercado, orden_callback: Callable[[str, float, int], None]):
        pass