from typing import cast
from sqlalchemy import create_engine
from . import Base
from sqlalchemy.orm import sessionmaker
from .model import Pending_Operation_Model,Reference_Price_Model


class StrategyA_DAO:
    
    def __init__(self, db_file):
        self.engine = create_engine(f'sqlite:///{db_file}')
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        print("Db Initialized")
        
    def get_pending_operations(self):
        session = self.Session()
        pending_operation = session.query(Pending_Operation_Model).all()
        session.close()
        return pending_operation

    def get_reference_price(self,id:int):
        session = self.Session()
        reference_price = cast(float | None, session.query(Reference_Price_Model).filter_by(id=id).first())
        session.close()
        return reference_price