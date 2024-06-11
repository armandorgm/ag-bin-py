from typing import List
from abc import ABC, abstractmethod
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
    
    def __init__(self,offset:float=None) -> None:
        self.offset = offset

    @abstractmethod
    def evaluar_orden(self, datos_mercado):
        pass