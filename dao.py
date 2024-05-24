from sqlalchemy import create_engine, Column, Integer, Float, String, Sequence,Boolean
#from sqlalchemy.ext.declarative import declarative_base #deprecated
from sqlalchemy.orm import declarative_base

from sqlalchemy.orm import sessionmaker
from models import OrderStatus,BotOperation,ProfitOperation
from sqlalchemy import or_

Base = declarative_base()

    
# DAO refactorizado
class OrderManagerDAO:
    def __init__(self, db_file):
        self.engine = create_engine(f'sqlite:///{db_file}')
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def storeNewOrder(self, id:int, status:str, operationId:int, type:str, reduceOnly:bool):
        session = self.Session()
        new_order = OrderStatus(id=id,status=status,operation_id=operationId,type=type,reduce_only=reduceOnly)
        session.add(new_order)
        session.commit()
        return new_order.id
    
    def storeNewProfitOperation(self, botOperationId:int, slotPrice:float, openOrderId:int=None, takeProfitOrderId:int=None):
        session = self.Session()
        existing_operation = (session.query(ProfitOperation)
            .filter_by(
                    bot_operation_id=botOperationId,
                    slot_price=slotPrice
            ).first())
        if existing_operation:
            existing_operation.open_order_id=openOrderId
            existing_operation.take_profit_order_id = takeProfitOrderId
        else:
            newProfitOperation = ProfitOperation(
                bot_operation_id=botOperationId,
                slot_price=slotPrice, 
                open_order_id=openOrderId, 
                take_profit_order_id=takeProfitOrderId
            )
            session.add(newProfitOperation)
        session.commit()
        return (existing_operation if existing_operation else newProfitOperation)
        
    def getProfitOperations(self):
        session = self.Session()
        profitOperation = session.query(ProfitOperation).all()
        session.close()
        return profitOperation
    def getProfitOperationsByOperationId(self, botOperationId):
        session = self.Session()
        profitOperation = session.query(ProfitOperation).filter_by(bot_operation_id=botOperationId).all()
        session.close()
        return profitOperation

    def closeFirstNonClosedProfitOperation(self, botOperationId:int, takeProfitOrderId:int):
        session = self.Session()
        profitOperation = (session.query(ProfitOperation)
        .filter(ProfitOperation.bot_operation_id == botOperationId)
        .order_by(ProfitOperation.open_order_id)
        .filter(
            ProfitOperation.open_order_id < takeProfitOrderId,
            ProfitOperation.take_profit_order_id.is_(None)).first()
        )
        if profitOperation is not None:
            # Update the takeProfitOrderId
            profitOperation.take_profit_order_id = takeProfitOrderId
            session.commit()
        else:
            print(f"No unclosed botOperationId found with id {botOperationId}")

    
    def registerNewOperation(self, entryPrice: float, symbol: str, longOrderId, shortOrderId):
        session = self.Session()
        new_operation = BotOperation(
            entry_price=entryPrice,
            symbol=symbol,
            long_entry_order_id=longOrderId,
            short_entry_order_id=shortOrderId
        )
        session.add(new_operation)
        session.commit()
        return new_operation.id

    def getBotOperations(self):
        session = self.Session()
        operations = session.query(BotOperation).filter(BotOperation.active).all()
        session.close()
        return operations
    
    def getBotOperation(self,operationId)->BotOperation:
        session = self.Session()
        operation = session.query(BotOperation).get(operationId)
        session.close()
        return operation
    
    def getOrderStatus(self,orderId:int)->OrderStatus:
        session = self.Session()
        orderStatus = session.query(OrderStatus).get(orderId)
        session.close()
        return orderStatus
    
    def getOperationOrdersByOperationId(self,operationId:int):
        session = self.Session()
        orderStatus = session.query(OrderStatus).join(BotOperation).filter(OrderStatus.operation_id == operationId, or_(OrderStatus.status == "closed", OrderStatus.status == "open")).all()
        session.close()
        return orderStatus
    


    # No necesitas definir __del__ para cerrar la sesión explícitamente
    # SQLAlchemy manejará la sesión por debajo

# Ejemplo de uso
if __name__ == "__main__":
    dao = OrderManagerDAO('order_manager.db')

    #dao.registerNewOperation(31.5864, "test", 1, 2)
    prompt = input("ingress an operation ID")
    orders = dao.getOperationOrdersByOperationId(int(prompt))
    for order in orders:
        print(order)
        #print((orderStatus.operation_id,orderStatus.status, botOperation.position_side))

        
    
