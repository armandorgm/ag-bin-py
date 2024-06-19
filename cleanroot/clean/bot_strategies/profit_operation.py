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

    def check_price(self, current_price:float):
        # Define la función lambda basada en el `position_side`
        if self.position_side.upper == 'LONG':
            print("checkeando operacion por cerrar", "LONG","Debug position side:",self.position_side)
            checker = lambda price: price >= self.close_price
        else:  # Asumiendo que la otra opción es 'SHORT'
            print("checkeando operacion por cerrar", "SHORT","Debug position side:",self.position_side)
            print("self.close_price_trigger:",self.close_price)
            checker = lambda price: price <= self.close_price
        return checker(current_price)