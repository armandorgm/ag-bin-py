from abc import ABC, abstractmethod
from typing import NamedTuple, Optional

from ..sql_models.models import strategy_config_model



class bot_dao_interface(ABC):
    @abstractmethod
    def registerOpenOperation(self):
        pass
    @abstractmethod
    def saveStrategyState(self,botId:int,strategyState:str):
        pass
    
    @abstractmethod
    def getBotStrategyConfig(self, botId:int)->Optional[strategy_config_model]:
        pass
    