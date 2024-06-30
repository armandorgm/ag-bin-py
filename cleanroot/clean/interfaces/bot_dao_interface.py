from abc import ABC, abstractmethod
from typing import NamedTuple, Optional

from ..bot_strategies.profit_operation import Profit_Operation

from ..sql_models.models import strategy_config_model



class bot_dao_interface(ABC):
    @abstractmethod
    def registerOpenOperation(self):
        pass
    
    @abstractmethod
    def saveStrategyState(self,botId:int,strategyState:str)->bool:
        pass
    
    @abstractmethod
    def getBotStrategyConfig(self, botId:int)->Optional[strategy_config_model]:
        pass
    @abstractmethod
    def get_pending_operations_for_bot(self,botId:int)->list[Profit_Operation]:
        pass
    @abstractmethod
    def delete_pending_operations(self,id:int)->bool:
        pass