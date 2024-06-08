from interfaces.exchange_basic import * 

class Order:
    def __init__(self,symbol:str,type:iOrderType,orderSide:iOrderSide,amount:float,positionSide:iPositionSide,price:Num =None) -> None:
        self.symbol = symbol
        self.type = type
        self.orderSide = orderSide
        self.amount = amount
        self.positionSide = positionSide
        self.price = price
        self.status:OrderStatus = "draft"
        pass
    

