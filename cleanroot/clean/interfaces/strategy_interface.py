from abc import ABC, abstractmethod
from decimal import Decimal

from sqlalchemy import create_engine

from .types import Fee, MarketInterface, Num, PositionSide

from ..bot_strategies.profit_operation import Profit_Operation
from ..bot_strategies.strategy_a.model import Profit_Operation_Model

class StrategyImplementor(ABC):
    @abstractmethod
    def saveStrategyState(self,strategyState):
        pass
    
    @property
    @abstractmethod
    def marketData(self)->MarketInterface:
        pass
    
class iStrategyA_DAO(ABC):
    
    @abstractmethod
    def create_pending_operations(self,exchangeId:str, amount:Num, position_side:PositionSide, entry_price:float, open_fee:Fee, closing_price:Decimal)->Profit_Operation:
        pass
    @abstractmethod
    def delete_pending_operations(self,id:int)->Profit_Operation:
        pass
    @abstractmethod
    def get_pending_operations(self)->list[Profit_Operation]:
        pass

        

