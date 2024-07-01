from unittest import IsolatedAsyncioTestCase,TestCase,skip
from unittest.mock import AsyncMock, MagicMock, Mock
from cleanroot.clean.bot_strategies.strategy_a.strategyA import StrategyA,StrategyStorage
from decimal import Decimal,getcontext

import pytest

from cleanroot.clean.interfaces.exchange_basic import ProfitOperation
context = getcontext()
context.prec = 16
class Test_StrategyA_general(IsolatedAsyncioTestCase):
    def setUp(self):
        #self.mock_interface = MagicMock()
        self.mock_interface = AsyncMock()
        
        self.offset = "2"
        self.rootCheckpoint="1"
        self.lastCheckpoint = "0.12336"
        positionSide1 = "long"
        
        dataStorage:StrategyStorage = {
            "positionSide": positionSide1,
            "offset": self.offset,
            "rootCheckpoint":self.rootCheckpoint,
            "lastCheckpoint":self.lastCheckpoint
        }
        self.longStrategy = StrategyA(self.mock_interface, dataStorage)  # Crea una instancia de StrategyA
    
            
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
        offset = "1.001"
        initialReferenceCheckpoint="0.12257"
        data:StrategyStorage = {
            "positionSide": positionSide1,
            "offset": offset,
            "rootCheckpoint":initialReferenceCheckpoint,
            "lastCheckpoint":"0.12336",
            "profit_operations":[]
        }
        longStrategy = StrategyA(mock_interface, data)  # Crea una instancia de StrategyA


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
        profitOperation:ProfitOperation={"checkpoint":Decimal("0.1300709963911075"),
                                          "openingOrderId":"111000",
                                          "closingOrderId":None}
        data:StrategyStorage = {
            "positionSide": "long",
            "offset": "1.001",
            "rootCheckpoint":"100",
            "lastCheckpoint":"100",
            "profit_operations":[profitOperation]
        }
        putOrder = AsyncMock()
        putOrder.return_value = {"info":{"clientOrderId":"123"}}
        mock_interface = AsyncMock()
        mock_interface.pricePrecision = 8
        mock_interface.amountPrecision = 8
        mock_interface.notionalMin = 5
        mock_interface.putOrder = putOrder
        mock_interface.strategyData = data
        mock_interface.saveStrategyState = Mock()
        async def fetch_order(foo):
            print("called with",end=" ")
            print(foo)
            return {"status":"closed"}
        mock_interface.fetch_order = fetch_order 
        
        

        longStrategy = StrategyA(mock_interface, data)  # Crea una instancia de StrategyA
           
        priceList:list[float] = [100,100.1,100.21,100,100.1,100.21]

        for newPrice in priceList:
            await longStrategy.evaluar_precio(Decimal(str(newPrice)))
        #longStrategy.interface.putOrder.assert_called()
        putOrder.assert_called()
        self.assertEqual(putOrder.call_count,2)

            

    