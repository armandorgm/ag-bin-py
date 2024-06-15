from typing import Literal, Union


class Profit_Operation:
    def __init__(self, entry_price, position_side:Union[Literal["LONG"],Literal["SHORT"]], close_price_trigger:float, amount):
        self.entry_price = entry_price
        self.position_side :Union[Literal["LONG"],Literal["SHORT"]]= position_side
        print(f"instanciando Profit_Operation close_price_trigger es = '{close_price_trigger}'",close_price_trigger)
        try:
            float(close_price_trigger)
        except Exception :
            print(Exception)
            print(type(close_price_trigger))
            print(close_price_trigger)
            raise Exception
        self.close_price_trigger = close_price_trigger
        self.open_fee = None
        self.close_fee = None
        self.amount = amount

    def check_price(self, current_price):
        # Define la función lambda basada en el `position_side`
        if self.position_side.upper == 'LONG':
            print("checkeando operacion por cerrar", "LONG","Debug position side:",self.position_side)
            checker = lambda price: price >= self.close_price_trigger
        else:  # Asumiendo que la otra opción es 'SHORT'
            print("checkeando operacion por cerrar", "SHORT","Debug position side:",self.position_side)
            print("self.close_price_trigger:",self.close_price_trigger)
            checker = lambda price: price <= self.close_price_trigger
        return checker(current_price)