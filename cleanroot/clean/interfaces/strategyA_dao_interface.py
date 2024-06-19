from abc import ABC, abstractmethod

from sqlalchemy import create_engine

from .types import Fee, Num, PositionSide

from ..bot_strategies.profit_operation import Profit_Operation
from ..bot_strategies.strategy_a.model import Profit_Operation_Model


class iStrategyA_DAO(ABC):
    
    @abstractmethod
    def create_pending_operations(self,exchangeId:str, amount:Num, position_side:PositionSide, entry_price:Num, open_fee:Fee, closing_price:float)->Profit_Operation:
        pass
    @abstractmethod
    def get_pending_operations(self)->list[Profit_Operation]:
        pass

        

