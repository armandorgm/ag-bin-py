from typing import Literal, Union, cast
from sqlalchemy import Column, Integer, String, Float, ForeignKey,Boolean
from . import Base


# Definir modelos
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



