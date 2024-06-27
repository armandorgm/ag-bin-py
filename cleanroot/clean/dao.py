from decimal import Decimal
import json
from typing import List, Union, cast
from sqlalchemy import create_engine, Column, Integer, Float, String, Sequence,Boolean

from .bot_strategies.profit_operation import Profit_Operation
from .interfaces.exchange_basic import Num
from .interfaces.types import Fee, PositionSide

from .interfaces.bot_dao_interface import bot_dao_interface
#from sqlalchemy.ext.declarative import declarative_base #deprecated
#from sqlalchemy.orm import declarative_base
from . import Base
# Base = declarative_base()

from sqlalchemy.orm import sessionmaker
from .sql_models.models import OrderStatus,BotOperation_model, Profit_Operation_Model,Strategy_model,Symbol_model, strategy_config_model
from sqlalchemy import or_


    
# DAO refactorizado
class OrderManagerDAO(bot_dao_interface):
    
    def __init__(self, db_file):
        self.engine = create_engine(f'sqlite:///{db_file}')
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        
    def getBotStrategyConfig(self,botId):
        session = self.Session()
        botOperation = session.query(strategy_config_model).filter_by(id=botId).first()
        if botOperation:
            return botOperation
        return None
    
    def saveStrategyState(self,botId,strategyState):
        #BotOperation_model
        session = self.Session()
        botOperation = session.query(BotOperation_model).filter_by(id=botId).first()
        if botOperation:
            botOperation.strategyState = strategyState
            session.commit()
            return True
        else:
            return False
        
    def get_strategies(self)->List[Strategy_model]:
        session = self.Session()
        strategies = session.query(Strategy_model).all()
        session.close()
        return strategies
    
    def get_symbols(self):
        session = self.Session()
        symbols = session.query(Symbol_model).all()
        session.close()
        return symbols
    
    def storeNewOrder(self, id:int, status:str, operationId:int, type:str, reduceOnly:bool):
        session = self.Session()
        new_order = OrderStatus(id=id,status=status,operation_id=operationId,type=type,reduce_only=reduceOnly)
        session.add(new_order)
        session.commit()
        return new_order.id
    
    def removeProfitOperation(self,profitOperationId:int):
        session = self.Session()
        try:
            profitOperation = session.query(ProfitOperation).filter_by(id=profitOperationId).first()
            if profitOperation:
                session.delete(profitOperation)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def storeNewProfitOperation(self, botOperationId:int, slotPrice:float, openOrderId:Union[int,None]=None, takeProfitOrderId:int|None=None):
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
    def getProfitOperationsByBotOperationId(self, botOperationId):
        session = self.Session()
        profitOperation = session.query(ProfitOperation).filter_by(bot_operation_id=botOperationId).all()
        session.close()
        return profitOperation
    def getProfitOperationByClosingOrderId(self,closingOrderId:int):
        session = self.Session()
        profitOperation = session.query(ProfitOperation).filter_by(take_profit_order_id=closingOrderId).first()
        session.close()
        return profitOperation
    def archiveProfitOperation(self,profitOperationId:int):
        session = self.Session()
        try:
            profitOperation = session.query(ProfitOperation).filter_by(id=profitOperationId).first()
            if profitOperation:
                session.delete(profitOperation)
                session.commit()
                return profitOperation
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
        

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
        new_operation = BotOperation_model(
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
        operations = session.query(BotOperation_model).filter(BotOperation_model.active).all()
        session.close()
        return operations
    
    def getBotOperation(self,operationId:int)->BotOperation_model|None:
        session = self.Session()
        operation = session.query(BotOperation_model).get(operationId)
        session.close()
        return operation
    
    def getOrderStatus(self,orderId:int)->OrderStatus:
        session = self.Session()
        orderStatus = session.query(OrderStatus).get(orderId)
        session.close()
        if orderStatus:
            return orderStatus
        raise BaseException(f"Failed to get order status with orderId:{orderId}")
    
    def getOperationOrdersByOperationId(self,operationId:int):
        session = self.Session()
        orderStatus = session.query(OrderStatus).join(BotOperation_model).filter(OrderStatus.operation_id == operationId, or_(OrderStatus.status == "closed", OrderStatus.status == "open")).all()
        session.close()
        return orderStatus

    def registerOpenOperation(self):
        raise NotImplementedError

    @staticmethod
    def profit_operation_parser(po:Profit_Operation_Model):
        return Profit_Operation(po.id, po.exchangeId,po.amount, po.position_side, po.entry_price,po.open_fee, po.closing_price,po.close_fee,po.status) # type: ignore
    
    def create_pending_operations(self,exchangeId:str, amount:Num, position_side:PositionSide, entry_price:float, open_fee:Fee, closing_price:Decimal)->Profit_Operation:
        session = self.Session()
        pending_operation = Profit_Operation_Model(exchangeId=exchangeId,position_side=position_side,amount=amount,entry_price=entry_price,open_fee=json.dumps(open_fee),closing_price=float(closing_price),close_fee=None,status="open")
        session.add(pending_operation)
        session.commit()
        return OrderManagerDAO.profit_operation_parser(pending_operation)
    
    def delete_pending_operations(self,id:int):
        session = self.Session()
        pending_operation = session.query(Profit_Operation_Model).filter_by(id=id).first()
        if pending_operation:
            # Elimina el objeto de la sesión
            session.delete(pending_operation)
            session.commit()
            print(f"Operación con ID {id} eliminada correctamente.")
            return True
        else:
            print(f"No se encontró ninguna operación con ID {id}.")
            return False

        
    def get_pending_operations_for_bot(self,botId:int)->list[Profit_Operation]:
        session = self.Session()
        pending_operation_model_list = session.query(Profit_Operation_Model).filter_by().all()
        session.close()
        
        pending_profit_operations:list[Profit_Operation]=[]
        for POM in pending_operation_model_list:
            pending_profit_operations.append(StrategyA_DAO.profit_operation_parser(POM))
        return pending_profit_operations



    


    # No necesitas definir __del__ para cerrar la sesión explícitamente
    # SQLAlchemy manejará la sesión por debajo

