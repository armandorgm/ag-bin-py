from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

from sqlalchemy import create_engine

from .types import Fee, MarketInterface, Num, Order, OrderSide, OrderType, PositionSide

from ..bot_strategies.profit_operation import Profit_Operation

class StrategyImplementor(ABC):
    
    @abstractmethod
    async def fetch_order(self,orderId:str)->Optional[Order]:
        pass
    
    @abstractmethod
    def saveStrategyState(self,strategyState:str):
        pass
    
    
    @property
    @abstractmethod
    def strategyData(self)->dict:
        pass
    
    @property
    @abstractmethod
    def marketData(self)->MarketInterface:
        pass
        
    @abstractmethod
    def create_pending_operations(self,exchangeId:str, amount:Num, position_side:PositionSide, entry_price:float, open_fee:Fee, closing_price:Decimal)->Profit_Operation:
        pass

    @abstractmethod
    async def putOrder(self, position_side:PositionSide|str, order_side:OrderSide, amount:Decimal, price:Decimal, orderType:OrderType)->Order:
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
        


