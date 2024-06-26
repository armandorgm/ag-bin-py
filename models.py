from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,sessionmaker

# Crea una instancia Base para declarar modelos
Base = declarative_base()

# Definir modelos
class BotOperation(Base):
    __tablename__ = 'bot_operations'
    id = Column(Integer, primary_key=True)
    entry_price = Column(Float, nullable=False)
    symbol = Column(String, nullable=False, unique=True)
    start_order_id = Column(Integer, nullable=False, unique=True)
    position_side = Column(String, nullable=False)
    active = Column(Boolean)
    threshold = Column(Integer)
    
    #Relations
    profit_operations = relationship("ProfitOperation", back_populates="bot_operation")
    orders = relationship("OrderStatus", back_populates="bot_operation")  
    
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
    bot_operation = relationship("BotOperation", back_populates="orders")

    #Representation
    def __repr__(self):
        return f"<OrderStatus(id={self.id}, status={self.status}, operation_id={self.operation_id}, type={self.type}, reduce_only={self.reduce_only})>"


class ProfitOperation(Base):
    __tablename__ = 'profit_operations'
    id = Column(Integer, primary_key=True, unique=True)
    bot_operation_id = Column(Integer, ForeignKey('bot_operations.id'), nullable=False,)
    slot_price = Column(Float, nullable=False)
    open_order_id = Column(Integer,unique=True)
    take_profit_order_id = Column(Integer,unique=True)
    #Relación 
    bot_operation  = relationship("BotOperation", back_populates="profit_operations")
    
    #def __init__(self,):
        

