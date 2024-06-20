from decimal import Decimal
from typing import Literal, Union
from..interfaces.exchange_basic import iProfit_Operation

class Profit_Operation:
    def __init__(
        self, 
        id:int,
        exchangeId:int,
        amount:Decimal,
        position_side: Union[
            Literal["LONG"],
            Literal["SHORT"]
        ],
        open_price:float,
        open_fee:float,
        close_price:Decimal,
        close_fee:float,
        status:iProfit_Operation
    ):
        self.id = id
        self.exchangeId = exchangeId
        self.amount = amount
        self.position_side :Union[Literal["LONG"],Literal["SHORT"]]= position_side
        self.open_price = open_price
        self.open_fee = open_fee
        self.close_price = close_price
        self.close_fee = None

    def check_price(self, current_price:Decimal):
        print("checkeando operacion por cerrar", current_price >= self.close_price)
        return current_price >= self.close_price