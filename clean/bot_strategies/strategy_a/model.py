from typing import Literal, Union, cast
from sqlalchemy import Column, Integer, String, Float, ForeignKey,Boolean
from . import Base


# Definir modelos
class Pending_Operation_Model(Base):
    __tablename__ = 'pending_operation'
    id = Column(Integer, primary_key=True)
    exchangeId = Column(Integer,nullable=False)
    position_side :Union[Literal["LONG"],Literal["SHORT"]]= Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    entry_price = Column(Float,nullable=False)
    open_fee = Column(Float,nullable=False)
    closing_price = Column(Float, nullable=True)
    close_fee = Column(Float,nullable=True)


class Reference_Price_Model(Base):
    __tablename__ = 'reference_price'
    id = Column(Integer, primary_key=True)
    price = Column(Float, nullable=False)

