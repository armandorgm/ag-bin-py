from bot_strategies.concrete_strategy import ConcreteStrategyA, ConcreteStrategyB
from strategy import Strategy
from models import BotOperation as BotOperationModel
from dao import OrderManagerDAO

class BotOperation:
    
    def getStrategy(strategyName):
        match strategyName:
            case "standard":
                return ConcreteStrategyA
            case _:
                raise "estrategia con nombre desconocido"
        pass
    def __init__(self,botOperationId: int,entry_price:float,position_side,symbol,threshold:float,strategyName) -> None:
        self.id = botOperationId
        self.entryPrice = entry_price
        self.positionSide = position_side
        self.symbol = symbol
        self.threshold = threshold
        self._strategy = BotOperation.getStrategy(strategyName)
        self.closingOrderPriceStrategy = None
        self.openingOrderAmountStrategy = None
        pass
    
    @property
    def strategy(self) -> Strategy:
        """
        The Context maintains a reference to one of the Strategy objects. The
        Context does not know the concrete class of a strategy. It should work
        with all strategies via the Strategy interface.
        """

        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """

        self._strategy = strategy

    def do_some_business_logic(self) -> None:
        """
        The Context delegates some work to the Strategy object instead of
        implementing multiple versions of the algorithm on its own.
        """

        # ...

        print("Context: Sorting data using the strategy (not sure how it'll do it)")
        result = self._strategy.do_algorithm(["a", "b", "c", "d", "e"])
        print(",".join(result))

        # ...
        
if __name__ == "__main__":
    # The client code picks a concrete strategy and passes it to the context.
    # The client should be aware of the differences between strategies in order
    # to make the right choice.

    context = BotOperation(ConcreteStrategyA())
    print("Client: Strategy is set to normal sorting.")
    context.do_some_business_logic()
    print()

    print("Client: Strategy is set to reverse sorting.")
    context.strategy = ConcreteStrategyB()
    context.do_some_business_logic()