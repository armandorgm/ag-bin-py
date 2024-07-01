from typing import Any, Awaitable, Callable, Literal, TypedDict,Union
from decimal import Decimal
from .types import Order,PositionSide,OrderSide,MarketInterface


iOrderType = Literal['limit', 'market', 'stopMarket']
#iPositionSide = Literal["LONG","SHORT"]
OrderStatus = Literal["draft"]
StrategyMessage = Literal["Mantener","Cerrar LONG y abrir nuevo LONG","Abrir LONG","Cerrar SHORT y abrir nuevo SHORT","Abrir Short"]
iProfit_Operation = Literal["open","closed"]
Num = Union[None, str, float, int, Decimal]

class iPosition(TypedDict):
    symbol: str
    order_type: str
    quantity: int
    side: str
    contracts:Any
class SymbolPrecision(TypedDict):
    amount:int
    base:int
    price:int 
    quote:int
    
iStrategy_Callback_Signal =  Callable[[str, str, Decimal, Decimal,iOrderType], Awaitable[Order]]

class ProfitOperation(TypedDict):
    checkpoint:Decimal
    openingOrderId:str
    closingOrderId:str|None