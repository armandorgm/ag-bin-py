import pandas as pd
from collections import deque

class EWMA_Calculator:
    def __init__(self, n):
        self.n = n
        self.precios = deque(maxlen=n)  # Lista de precios con tamaño máximo n
        self.ewma = None  # Valor EWMA calculado

    def new_price(self, nuevo_precio):
        self.precios.append(nuevo_precio)  # Agregar el nuevo precio
        if len(self.precios) >= self.n:
            self.calcular_ewma()  # Calcular el EWMA si hay suficientes datos
            return self.ewma[-1]  # Retornar el último valor del EWMA
        else:
            return None  # No hay suficientes datos para calcular el EWMA

    def calcular_ewma(self):
        if len(self.precios) < self.n:
            print("No hay suficientes datos para calcular el EWMA.")
            return

        # Calcular el EWMA
        self.ewma = pd.Series(self.precios).ewm(span=self.n).mean()

# Ejemplo de uso
mi_calculadora_ewma = EWMA_Calculator(n=5)
print(mi_calculadora_ewma.new_price(9))  # None (no hay suficientes datos)
print(mi_calculadora_ewma.new_price(5))  # None (no hay suficientes datos)
print(mi_calculadora_ewma.new_price(10))  # None (no hay suficientes datos)
print(mi_calculadora_ewma.new_price(16))  # None (no hay suficientes datos)
print(mi_calculadora_ewma.new_price(5))  # 8.971564 (valor EWMA calculado)

# Puedes seguir agregando más precios con mi_calculadora_ewma.new_price(nuevo_precio)
