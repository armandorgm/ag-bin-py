from dao import OrderManagerDAO
from  ccxt.pro import binanceusdm
from ccxt.base.types import Order
from pprint import pprint

from sql_models.models import BotOperation_model, OrderStatus

class DbIntegrity:
    def __init__(self, dao:OrderManagerDAO, exchange:binanceusdm):
        self.dao = dao
        self.exchange = exchange
    
    async def checkOrderStatusIntegrityForOperationId(self,operationId):
        operation = self.dao.getBotOperation(operationId)
        orders = await self.exchange.fetch_orders(operation.symbol,None,None,{})
        orders:list[Order] = list(filter(lambda order:order['info']["positionSide"] == operation.position_side,orders))
        for order in orders:
            pprint(("remote:",order['info']["positionSide"],"db:",operation.position_side))
            result =self.dao.getOrderStatus(order["id"])
            if result == None:
                #pprint(order)
                #prompt = input(f"there are missing {order["symbol"]} orders in db from side {order["info"]["positionSide"]}\nDo you want to store missing data?")
                #if(prompt):
                self.dao.storeNewOrder(order["id"],order["status"],operationId, order["type"], order["reduceOnly"])

        startOrder = await self.exchange.fetch_order(str(operation.start_order_id),str(operation.symbol))
        if startOrder["status"] =="closed":
            orders = await self.exchange.fetch_orders(operation.symbol,None,None,{})
            pprint(("size:",len(orders)))
            pprint((orders[0]['info']["positionSide"], startOrder["info"]["positionSide"]))
            orders = list(filter(lambda order:order['info']["positionSide"] == startOrder["info"]["positionSide"],orders))
            pprint(("size:",len(orders)))

            for order in orders:
                pprint((order['datetime'],order['side'],order["price"],order["reduceOnly"],order["type"],order["status"]))
            #pprint(orders)
        
    async def checkDbIntegrity(self):
        operations = self.dao.getBotOperations()
        for operation in operations:
            await self.checkOrderStatusIntegrityForOperationId(operation.id)
            await self.poblateOpenCloseOperations(operation.id)
    
    async def poblateOpenCloseOperations(self,operationId):
        print("poblateOpenCloseOperations:")
        operation = self.dao.getBotOperation(operationId)
        orders = self.dao.getOperationOrdersByOperationId(operation.id)
        for order in orders:
            if(order.reduce_only == 0):
                self.dao.storeNewProfitOperation(order.operation_id,order.id)
            else:
                self.dao.closeFirstNonClosedProfitOperation(order.operation_id,order.id)


            
#pending
        
    
        


            
                    