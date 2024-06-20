from typing import Union, cast
from sqlalchemy import Column, Integer, String, Float, ForeignKey,Boolean
#from sqlalchemy.ext.declarative import declarative_base
#Base = declarative_base()
from .. import Base
from sqlalchemy.orm import relationship

# Crea una instancia Base para declarar modelos

# Definir modelos
class BotOperation_model(Base):
    __tablename__ = 'bot_operations'
    id:int = Column(Integer, primary_key=True) # type: ignore
    entry_price = Column(Float, nullable=False)
    symbol:str = Column(String, nullable=False, unique=True) # type: ignore
    #position_side = Column(String, nullable=False)
    active = Column(Boolean)
    threshold:str = Column(Float, nullable=False) # type: ignore
    name = Column(String, nullable=False, unique=True)
    strategyOpId:int = Column(Integer,ForeignKey('strategies.id'),nullable=False) # type: ignore
    
    #Relations
    #profit_operations = relationship("ProfitOperation", back_populates="bot_operation")
    #orders = relationship("OrderStatus", back_populates="bot_operation")  
    
    #Representation
    def __repr__(self):
        return f"<BotOperation(id={self.id}, entry_price={self.entry_price}, symbol={self.symbol}, start_order_id={self.start_order_id}, position_side={self.position_side}, active={self.active})>"

class OrderStatus(Base):
    __tablename__ = 'order_status'
    id = Column(Integer, primary_key=True, unique=True)
    status = Column(String)
    operation_id = Column(Integer, ForeignKey('bot_operations.id'), nullable=False)
    type = Column(String)
    reduce_only = Column(Boolean)
    
    # Relaciónes
    #bot_operation = relationship("BotOperation_model", back_populates="orders")

    #Representation
    def __repr__(self):
        return f"<OrderStatus(id={self.id}, status={self.status}, operation_id={self.operation_id}, type={self.type}, reduce_only={self.reduce_only})>"


class ProfitOperation(Base):
    __tablename__ = 'profit_operations'
    id = cast(int,Column(Integer, primary_key=True, unique=True))
    bot_operation_id = Column(Integer, ForeignKey('bot_operations.id'), nullable=False,)
    slot_price = Column(Float, nullable=False)
    _open_order_id = Column(Integer,unique=True,nullable=True)
    take_profit_order_id = Column(Integer,unique=True,nullable=True)
    #Relación 
    #bot_operation  = relationship("BotOperation_model", back_populates="profit_operations")
    
    #def __init__(self,):
    
class Strategy_model(Base):
    __tablename__ = 'strategies'
    id = cast(int,Column(Integer, primary_key=True, unique=True))
    name = cast(str,Column(String, nullable=False))
    
    def __repr__(self):
        return f"{self.id}, {self.name}"

class Symbol_model(Base):
    __tablename__ = 'symbols'
    id = cast(int,Column(Integer, primary_key=True, unique=True))
    name = cast(str,Column(String, nullable=False))
    
