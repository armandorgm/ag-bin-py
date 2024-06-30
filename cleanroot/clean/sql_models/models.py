from typing import Union, cast
from sqlalchemy import Column, Integer, String, Float, ForeignKey,Boolean
#from sqlalchemy.ext.declarative import declarative_base
#Base = declarative_base()
from .. import Base

# Crea una instancia Base para declarar modelos

# Definir modelos
    
class BotOperation_model(Base):
    __tablename__ = 'bot_operations'
    id:int = Column(Integer, primary_key=True) # type: ignore
    symbol:str = Column(String, nullable=False, unique=True) # type: ignore
    active = Column(Boolean)
    description:str = Column(String, nullable=False, unique=True) # type: ignore
    strategy_config_id:int = Column(Integer,ForeignKey('strategies.id'),nullable=False) # type: ignore
        
    def __repr__(self):
        return f"<BotOperation(id={self.id}, symbol={self.symbol}, active={self.active})>"

class OrderStatus(Base):
    __tablename__ = 'order_status'
    id = Column(Integer, primary_key=True, unique=True)
    status = Column(String)
    operation_id = Column(Integer, ForeignKey('bot_operations.id'), nullable=False)
    type = Column(String)
    reduce_only = Column(Boolean)

    def __repr__(self):
        return f"<OrderStatus(id={self.id}, status={self.status}, operation_id={self.operation_id}, type={self.type}, reduce_only={self.reduce_only})>"


class ProfitOperation_Model_archive1(Base):
    __tablename__ = 'profit_operations'
    id:int = Column(Integer, primary_key=True, unique=True) # type: ignore
    bot_operation_id:int = Column(Integer, ForeignKey('bot_operations.id'), nullable=False,) # type: ignore
    slot_price = Column(Float, nullable=False)
    _open_order_id:str = Column(String,unique=True,nullable=True) # type: ignore
    take_profit_order_id:str = Column(String,unique=True,nullable=True) # type: ignore
    
class Profit_Operation_Model(Base):
    __tablename__ = 'pending_operation'
    id = Column(Integer, primary_key=True)
    exchangeId = Column(String,nullable=False)
    amount = Column(Float, nullable=False)
    position_side = Column(String, nullable=False)
    entry_price = Column(Float,nullable=False)
    open_fee = Column(String,nullable=False)
    closing_price = Column(Float, nullable=True)
    close_fee = Column(Float,nullable=True)
    status = Column(String,nullable=False)
    botId = Column(Integer,ForeignKey("bot_operations.id"),nullable=False)
    strategyConfigId=Column(Integer,ForeignKey("strategy_config.id"),nullable=False)

class Symbol_model(Base):
    __tablename__ = 'symbols'
    id:int = Column(Integer, primary_key=True, unique=True) # type: ignore
    name:str = Column(String, nullable=False) # type: ignore
    
class strategy_config_model(Base):
    __tablename__ = 'strategy_config'
    id:int = Column(Integer, primary_key=True, unique=True) # type: ignore
    strategy_id = Column(String, nullable=False)
    data:str = Column(String, nullable=False) # type: ignore
    