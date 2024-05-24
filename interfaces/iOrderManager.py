from abc import ABC, abstractmethod
from ccxt.base.types import OrderType,OrderSide,PositionSide,Order

class iOrderManager(ABC):
    @abstractmethod
    async def startMenu(self):
        pass
    @abstractmethod
    async def monitor_order(self, order_id, symbol):
        pass       
    @abstractmethod          
    async def getMinAmountAtMarketPrice(self,symbol,side:OrderSide) -> int:
        pass
    @abstractmethod          
    async def testFuction(self):
        pass        
    @abstractmethod          
    async def createOpositeOrder(self, order:Order)->Order:
        pass
    @abstractmethod          
    async def createNewBotOperation(self):
            pass
    @abstractmethod          
    async def createOrder(self):
        pass
    @abstractmethod          
    async def createOrderV2(self, symbol, type:OrderType, side:OrderSide, amoung:float, price:float, positionSide:PositionSide) -> Order:
        pass    
    @abstractmethod          
    def create_profit_operation(self, botOperationId:int, slotPrice:float, positionSide:PositionSide):
        pass  
    @abstractmethod          
    async def monitor_order_and_create_second(self, order_id,symbol,type,side,amount,price, positionSide):
        pass
    @abstractmethod          
    async def create_take_profit_order(self, openOrder):
        pass
    @abstractmethod          
    async def showOpenPosition(self):
        pass
    @abstractmethod          
    async def myPositions(self):
        pass