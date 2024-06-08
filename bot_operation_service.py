from asyncio import sleep
import asyncio
from pprint import pprint
from bot_strategies.concrete_strategy import EstrategiaLong,EstrategiaShort
from strategy import Strategy
from ccxt.pro import binanceusdm
#from models import BotOperation as BotOperationModel
#from dao import OrderManagerDAO
from bot import Bot
from interfaces.exchange_basic import iPositionSide
class BotOperation(Bot):
    
    @staticmethod
    def startMenu():
        selection = input(""""
                          Select an option:
                          
                          """)
    
    def getStrategy(strategyName)->Strategy:
        match strategyName:
            case "standard":
                pass
                #return ConcreteStrategyA
            case _:
                raise "estrategia con nombre desconocido"
        pass
    def __init__(self, 
                 exchange:binanceusdm, 
                 position_side:iPositionSide, 
                 symbol:str, 
                 threshold:float,
                 strategyName,
                 name:str) -> None:
        
        super().__init__(name)
        self.status = 0
        self.exchange = exchange
        self.entryPrice :float
        self.positionSide = position_side
        self.symbol = symbol
        self.threshold = threshold
        #self._strategy = BotOperation.getStrategy(strategyName)()
        self._strategy = EstrategiaLong()
        self.closingOrderPriceStrategy = None
        self.openingOrderAmountStrategy = None
        self.numero_ordenes_contra = 0  # Contador para las órdenes contrarias consecutivas

        pass
    
    def actualizar_datos(self, datos_mercado):
        accion, precio_entrada = self._strategy.evaluar_orden(datos_mercado, self.entryPrice, self.threshold)
        
        if accion == 'Cerrar LONG y abrir nuevo LONG':
            self.cerrar_orden()
            self.abrir_orden('LONG', datos_mercado['precio_actual'])
        elif accion == 'Abrir LONG':
            self.abrir_orden('LONG', datos_mercado['precio_actual'])
            self.numero_ordenes_contra += 1
            if self.numero_ordenes_contra >= 2:  # Cambiar a estrategia SHORT después de 2 movimientos contrarios consecutivos
                print("Precio giró en contra. offset:",self.numero_ordenes_contra)
                self.cambiar_estrategia(EstrategiaShort())
                self.numero_ordenes_contra = 0
        elif accion == 'Mantener':
            pass
        elif accion == 'Cerrar SHORT y abrir nuevo SHORT':
            self.cerrar_orden()
            self.abrir_orden('SHORT', datos_mercado['precio_actual'])

        elif accion == "Abrir Short":
            print("Precio giró en contra")
            self.abrir_orden('SHORT', datos_mercado['precio_actual'])
            self.numero_ordenes_contra += 1
            if self.numero_ordenes_contra >= 2:  # Cambiar a estrategia SHORT después de 2 movimientos contrarios consecutivos
                self.cambiar_estrategia(EstrategiaLong())
                self.numero_ordenes_contra = 0
            

    def abrir_orden(self, tipo, precio_actual):
        self.precio_entrada = precio_actual
        print(f'Abrir {tipo} a precio {precio_actual}')
        
    def cerrar_orden(self):
        print('Cerrar orden actual')

    def cambiar_estrategia(self, nueva_estrategia):
        self._strategy = nueva_estrategia
        print('Cambiando estrategia a:',nueva_estrategia)

    
    async def start(self):
        
        super().start()
        self.status = 1
        #self.exchange.verbose = True
        entryReferencePrice = (await self.exchange.watch_ticker(self.symbol))['last']
        self.entryPrice = entryReferencePrice
        pprint(entryReferencePrice)
        self.exchange.verbose = False
        while self.status:
            try:
                lastPrice = (await self.exchange.watch_ticker(self.symbol))['last']
                pprint(lastPrice)
                self.actualizar_datos({"precio_actual":lastPrice})

                #pprint(await self.exchange.watch_ohlcv(self.symbol,"1m",None,5))
                #pprint((await self.exchange.watch_order_book(self.symbol,5))["asks"][0])
            except KeyboardInterrupt:
                await self.exchange.close()
            finally:
                await asyncio.sleep(1)
                pass
        await self.exchange.close()

        
    @property
    def strategy(self) -> Strategy:
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """

        self._strategy = strategy

    
        
"""
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
"""