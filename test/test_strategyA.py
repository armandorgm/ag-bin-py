from unittest import IsolatedAsyncioTestCase,TestCase,skip
from unittest.mock import AsyncMock, MagicMock
from cleanroot.clean.bot_strategies.strategy_a.strategyA import StrategyA
from decimal import Decimal,getcontext

import pytest
context = getcontext()
context.prec = 16
class Test_StrategyA_general(IsolatedAsyncioTestCase):
    def setUp(self):
        #self.mock_interface = MagicMock()
        self.mock_interface = AsyncMock()
        self.offset = "2"
        self.rootCheckpoint=Decimal("1")
        self.lastCheckpoint = "0.12336"
        
        positionSide1 = "long"
        self.longStrategy = StrategyA(self.mock_interface, positionSide1, self.offset,self.rootCheckpoint, self.lastCheckpoint)  # Crea una instancia de StrategyA
    
        
        positionSide2 = "short"
        #self.shortStrategy = StrategyA(self.mock_interface, positionSide2, self.offset,self.initialReferenceCheckpoint)  # Crea una instancia de StrategyA

    
    #@skip("Esta prueba está deshabilitada temporalmente")
    def test_ref_price_initialization(self):

        precision = Decimal("0.00000001")
        # Verifica que la referencia de precio se inicialice correctamente
        # strategy.lastCheckpoint, 
        # strategy.rootCheckpoint
        self.assertEqual(self.longStrategy.nextCheckpoint, Decimal((self.longStrategy.offset)*self.longStrategy.lastCheckpoint))
        self.assertEqual(self.longStrategy.previousCheckpoint.quantize(precision), Decimal(self.longStrategy.lastCheckpoint/(self.longStrategy.offset))) # type: ignore
    
    def test_backAndFordwardCheckpoints(self):
        times = 5000
        upperThousandTimes = Decimal(100)
        for _ in range(times):
            upperThousandTimes = self.longStrategy._getFollowingCheckpointPrice(upperThousandTimes)
        #print(upperThousandTimes)
        for _ in range(times):
            upperThousandTimes = self.longStrategy._getPreviousCheckpointPrice(upperThousandTimes) 
        self.assertEqual(upperThousandTimes,Decimal(100))
    
    def test_calcular_saltos_en_progresion(self):
        rootCheckpoint = Decimal(self.longStrategy.rootCheckpoint)
        self.assertEqual(self.longStrategy.calcular_saltos_en_progresion(rootCheckpoint,self.longStrategy.getNthProgresionValueFromCheckpoint(5000,self.longStrategy.rootCheckpoint)),5000)
    
    def test_getMakerPrice(self):
        self.mock_interface.pricePrecision = 1
        self.assertEqual(self.longStrategy.getMakerPrice(Decimal("0.5")),Decimal("0.4"))
        #self.assertEqual(self.shortStrategy.getMakerPrice(Decimal("0.5")),Decimal("0.6"))

        pass
    
    def test_getNthProgresionValueFromCheckpoint(self):
        self.assertEqual(self.longStrategy.getNthProgresionValueFromCheckpoint(1,self.longStrategy.rootCheckpoint),2)
        self.assertEqual(self.longStrategy.getNthProgresionValueFromCheckpoint(2,self.longStrategy.rootCheckpoint),4)
        self.assertEqual(self.longStrategy.getNthProgresionValueFromCheckpoint(3,self.longStrategy.rootCheckpoint),8)

    async def test_evaluar_precio(self):
        print("\n")
        #self.mock_interface.tick =Decimal(0.1)
        self.mock_interface.pricePrecision = 0
        #self.mock_interface.get_min_amount.return_value = Decimal("0.00000001")
        self.mock_interface.amountPrecision = 8
        self.mock_interface.notionalMin = 5
        
            
        newPrice = Decimal(109)

                
        # Ejecuta la evaluación de precio
        #orden de argumentos de putOrder:
        #position_side, order_side, amount, price, orderType
        
        precioEtapa = self.longStrategy.lastCheckpoint
        print("\n\n##Etapa1 Evaluar precio##",precioEtapa)
        await self.longStrategy.evaluar_precio(precioEtapa)
        self.longStrategy.interface.putOrder.assert_not_called()

        precioEtapa = self.longStrategy.getNthProgresionValueFromCheckpoint(1,self.longStrategy.rootCheckpoint)
        print("\n\n##Etapa2 Evaluar precio##",precioEtapa)
        await self.longStrategy.evaluar_precio(precioEtapa)
        self.longStrategy.interface.putOrder.assert_not_called()

        precioEtapa = self.longStrategy.getNthProgresionValueFromCheckpoint(2,self.longStrategy.rootCheckpoint)
        print("\n\n##Etapa3 Evaluar precio##",precioEtapa)
        await self.longStrategy.evaluar_precio(precioEtapa)

        self.longStrategy.interface.putOrder.assert_called_with("long","buy",Decimal("1.66666667"),Decimal(3),"limit")
        # Verifica que se haya llamado a la función de orden correctamente
    
    
    
            
    def test_updateReferencePrice(self):
        testNumber = 3
        strategy = self.longStrategy
        currentCheckpoint = strategy.lastCheckpoint
        # strategy.lastCheckpoint, 
        # strategy.rootCheckpoint
        self.assertEqual(strategy.nextCheckpoint, currentCheckpoint*(strategy.offset))
        self.assertEqual(strategy.previousCheckpoint, currentCheckpoint/(strategy.offset))

        strategy.updatePriceCheckpoints(testNumber)
        self.assertEqual(strategy.lastCheckpoint, currentCheckpoint*((strategy.offset)**testNumber))
        self.assertEqual(strategy.nextCheckpoint, currentCheckpoint*((strategy.offset)**(testNumber+1)))
        self.assertEqual(strategy.previousCheckpoint, currentCheckpoint*((strategy.offset)**(testNumber-1)))
    
class Test_StrategyA_isolated(IsolatedAsyncioTestCase):
    
    def test_calcular_saltos_en_progresion(self):
        print("\n Test test_calcular_saltos_en_progresion starts")
        mock_interface = MagicMock()
        mock_interface.pricePrecision = 0
        mock_interface.amountPrecision = 8
        mock_interface.notionalMin = 5
        positionSide1 = "long"
        offset = Decimal(str(0.1/100))
        initialReferenceCheckpoint=Decimal("0.12257")
        longStrategy = StrategyA(mock_interface, positionSide1, offset, initialReferenceCheckpoint,"0.12336")  # Crea una instancia de StrategyA


        currentCheckpoint = Decimal(longStrategy.lastCheckpoint)
        priceList:list[float] = [0.12336,0.12335,0.12337,0.12338,0.12337]
        for newPrice in priceList:
            if newPrice == priceList[0]:
                self.assertEqual(longStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),0)
            elif newPrice == priceList[1]:
                self.assertEqual(longStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),0)
            elif newPrice == priceList[2]:
                self.assertEqual(longStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),0)
    
    
    async def test_evaluar_precio2(self):
        putOrder = AsyncMock()
        mock_interface = AsyncMock()
        mock_interface.pricePrecision = 8
        mock_interface.amountPrecision = 8
        mock_interface.notionalMin = 5
        mock_interface.putOrder = putOrder

        positionSide1 = "long"
        offset = "1.001"
        initialReferenceCheckpoint=Decimal("0.12257")
        longStrategy = StrategyA(mock_interface, positionSide1, offset, initialReferenceCheckpoint,"0.12336")  # Crea una instancia de StrategyA
           
        priceList:list[float] = [0.12336,0.12335,0.12337,0.12338,0.12337,0.13,0.14,0.15]

        for newPrice in priceList:
            await longStrategy.evaluar_precio(Decimal(str(newPrice)))
        #longStrategy.interface.putOrder.assert_called()
        putOrder.assert_called()
        self.assertEqual(putOrder.call_count,2)

            

    