from typing import Any, Literal, TypedDict,Union
from decimal import Decimal


iOrderType = Literal['limit', 'market', 'stopMarket']
iOrderSide = Literal["buy","sell"]
iPositionSide = Literal["LONG","SHORT"]
OrderStatus = Literal["draft"]
StrategyMessage = Literal["Mantener","Cerrar LONG y abrir nuevo LONG","Abrir LONG","Cerrar SHORT y abrir nuevo SHORT","Abrir Short"]

Num = Union[None, str, float, int, Decimal]

class iPosition(TypedDict):
    symbol: str
    order_type: str
    quantity: int
    side: str
    contracts:Any
    