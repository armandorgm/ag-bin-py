from abc import ABC, abstractmethod
from decimal import Decimal

from sqlalchemy import create_engine

from .types import Fee, MarketInterface, Num, Order, OrderType, PositionSide

from ..bot_strategies.profit_operation import Profit_Operation

class StrategyImplementor(ABC):
    @abstractmethod
    def saveStrategyState(self,strategyState):
        pass
    
    @property
    @abstractmethod
    def marketData(self)->MarketInterface:
        pass
        
    @abstractmethod
    def create_pending_operations(self,exchangeId:str, amount:Num, position_side:PositionSide, entry_price:float, open_fee:Fee, closing_price:Decimal)->Profit_Operation:
        pass
   
    @abstractmethod
    def get_pending_operations(self)->list[Profit_Operation]:
        pass

    @abstractmethod
    def putOrder(self, position_side, order_side, amount, price,orderType:OrderType)->Order:
        pass
    
    @property
    @abstractmethod
    def tick(self)->Decimal:
        pass
    
    @property
    @abstractmethod
    def notionalMin(self)->Decimal:
        pass
    @abstractmethod
    def amountPrecision(self)->int:
        pass
    
    @property
    @abstractmethod
    def pricePrecision(self)->int:
        pass
        


