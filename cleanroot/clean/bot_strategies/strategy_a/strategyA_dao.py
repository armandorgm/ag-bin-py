from decimal import Decimal

from sqlalchemy import create_engine

from ...interfaces.strategyA_dao_interface import iStrategyA_DAO

from ...interfaces.types import Fee, Num, PositionSide

from ...bot_strategies.profit_operation import Profit_Operation
from . import Base
from sqlalchemy.orm import sessionmaker
from .model import Profit_Operation_Model


class StrategyA_DAO(iStrategyA_DAO):
    
    def __init__(self, db_file):
        self.engine = create_engine(f'sqlite:///{db_file}')
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        print("Db Initialized")
        
    @staticmethod
    def profit_operation_parser(po:Profit_Operation_Model):
        return Profit_Operation(po.id, po.exchangeId,po.amount, po.position_side, po.entry_price,po.open_fee, po.closing_price,po.close_fee,po.status) # type: ignore
    
    def create_pending_operations(self,exchangeId:str, amount:Num, position_side:PositionSide, entry_price:Num, open_fee:Fee, closing_price:float)->Profit_Operation:
        session = self.Session()
        pending_operation = Profit_Operation_Model(exchangeId=exchangeId,position_side=position_side,amount=amount,entry_price=entry_price,open_fee=open_fee,closing_price=closing_price,close_fee=None,status="open")
        session.add(pending_operation)
        session.commit()
        return StrategyA_DAO.profit_operation_parser(pending_operation)
    
    def get_pending_operations(self)->list[Profit_Operation]:
        session = self.Session()
        pending_operation_model_list = session.query(Profit_Operation_Model).all()
        session.close()
        
        pending_profit_operations:list[Profit_Operation]=[]
        for POM in pending_operation_model_list:
            pending_profit_operations.append(StrategyA_DAO.profit_operation_parser(POM))
        return pending_profit_operations

