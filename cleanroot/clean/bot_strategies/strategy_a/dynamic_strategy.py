
import simplejson as json
from cleanroot.clean.bot_strategies.strategy_a.strategyA import StrategyA, StrategyStorage
from cleanroot.clean.interfaces.exchange_basic import ProfitOperation
from cleanroot.clean.interfaces.strategy_interface import StrategyImplementor


class StrategyStorage2(StrategyStorage):
    offset:str
    positionSide:str
    positionSideType:str
    lastCheckpoint:str
    rootCheckpoint:str
    profit_operations:list[ProfitOperation]
    consecutives_price_fordward:int
    
class Dynamic_Strategy(StrategyA):
    id:int = 3
    name:str = "Estrategia_Dinamica"
    
    #def __init__(self, interface:StrategyImplementor, positionSide:PositionSide, offset:int|str|Decimal,rootCheckpoint:int|str|Decimal,lastCheckpoint:str) -> None:
    def __init__(self, interface:StrategyImplementor, data:StrategyStorage) -> None:
        super().__init__(interface=interface,data=data)
        self.positionSideType = data["positionSideType"] if "positionSideType" in data else "fixed"
    
    @property
    def cacheData(self):
        data:StrategyStorage = {
            "positionSide":str(self.positionSide),
            "offset":str(self.offset),
            "rootCheckpoint":str(self.rootCheckpoint),
            "lastCheckpoint":str(self.lastCheckpoint),
            "profit_operations":self._profitOperations,
            "consecutives_price_fordward":self.consecutives_price_fordward,
            "positionSideType":self.positionSideType
        }
        return json.dumps(data)
    
    async def evaluar_precio(self, receivedPrice:Decimal):
        try:
           pass
        except Exception as e:
            print(e)
            print("ERROR: Evaluando precio. Skiping...")