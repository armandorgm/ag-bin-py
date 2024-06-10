"""
Concrete Strategies implement the algorithm while following the base Strategy
interface. The interface makes them interchangeable in the Context.
"""


from typing import List, Union
from interfaces.exchange_basic import StrategyMessage
from bot_strategies.strategy import Strategy

"""
class ConcreteStrategyA(Strategy):
    def do_algorithm(self, data: List) -> List:
        return sorted(data)
"""

"""
class ConcreteStrategyB(Strategy):
    def do_algorithm(self, data: List) -> List:
        return reversed(sorted(data))
"""

class EstrategiaLong(Strategy):

    def evaluar_orden(self, datos_mercado, precio_entrada, porcentaje):
        # Aquí implementamos la lógica de la orden LONG
        precio_objetivo = precio_entrada * (1 + porcentaje / 100)
        precio_margen = precio_entrada * (1 - porcentaje / 100)
        print("precio_objetivo",precio_objetivo)

        if datos_mercado['precio_actual'] >= precio_objetivo:
            return 'Cerrar LONG y abrir nuevo LONG', precio_objetivo
        elif datos_mercado['precio_actual'] <= precio_margen:
            return 'Abrir LONG', precio_margen
        else:
            return 'Mantener', None

class EstrategiaShort(Strategy):

    def evaluar_orden(self, datos_mercado, precio_entrada, porcentaje)->tuple[StrategyMessage,Union[float,None]]:
        # Aquí implementamos la lógica de la orden SHORT
        precio_objetivo = precio_entrada * (1 - porcentaje / 100)
        precio_margen = precio_entrada * (1 + porcentaje / 100)
        print("precio_objetivo",precio_objetivo)

        
        if datos_mercado['precio_actual'] <= precio_objetivo:
            return 'Cerrar SHORT y abrir nuevo SHORT', precio_objetivo
        elif datos_mercado['precio_actual'] >= precio_margen:
            return 'Abrir Short', precio_margen
        else:
            return 'Mantener', None
