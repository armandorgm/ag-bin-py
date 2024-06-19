from typing import Literal

class UserInterface:
    def __init__(self, symbols):
        self.symbols = symbols

    def select_symbol(self):
        # ... (implementation for symbol selection)
        for index, value in enumerate(self.symbols, start=1):  # Empezar el índice en 1
            print(f"{index}) {value}")  # Imprimir el menú
        selected = int(input("input a symbol number\n"))
        print("selected: " +self.symbols[selected-1])
        return self.symbols[selected-1]

    def selectPositionSide(self) -> Literal["LONG","SHORT","BOTH"]:
        positionSide=["LONG","SHORT","BOTH"]
        for index, value in enumerate(positionSide, start=1):  # Empezar el índice en 1
            print(f"{index}) {value}")  # Imprimir el menú
        selected = int(input("input the positionSide number\n"))
        print("selected: " +positionSide[selected-1])
        return positionSide[selected-1]
