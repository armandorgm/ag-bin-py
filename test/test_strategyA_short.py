from unittest import IsolatedAsyncioTestCase,TestCase,skip
from unittest.mock import AsyncMock, MagicMock, Mock
from cleanroot.clean.bot_strategies.strategy_a.strategyA import StrategyA,StrategyStorage
from decimal import Decimal

import pytest

from cleanroot.clean.interfaces.exchange_basic import ProfitOperation
class Test_StrategyA_general(IsolatedAsyncioTestCase):
    def setUp(self):
        #self.mock_interface = MagicMock()
        self.mock_interface = AsyncMock()
        #self.mock_interface.strategyData = {}
        self.mock_interface.putOrder.return_value = {"info":{"clientOrderId":"xxx"}} #required by [evaluar_precio]
        self.mock_interface.pricePrecision = 8 #required by[test_backAndFordwardCheckpoints]
        
        self.offset = "1.001"
        self.rootCheckpoint="100"
        self.lastCheckpoint = "100"
        positionSide1 = "short"
        
        dataStorage:StrategyStorage = {
            "positionSide": positionSide1,
            "offset": self.offset,
            "rootCheckpoint":self.rootCheckpoint,
            "lastCheckpoint":self.lastCheckpoint,
            "consecutives_price_fordward":0,
            "profit_operations":[]
        }
        self.shortStrategy = StrategyA(self.mock_interface, dataStorage)  # Crea una instancia de StrategyA
    
    
    #@skip("Esta prueba está deshabilitada temporalmente")
    def test_ref_price_initialization(self):

        self.assertEqual(self.shortStrategy.nextCheckpoint, Decimal('99.90009990'))
        self.assertEqual(self.shortStrategy.previousCheckpoint, Decimal(self.shortStrategy.lastCheckpoint*(self.shortStrategy.offset))) # type: ignore
    
    def test_backAndFordwardCheckpoints(self):
        times = 100
        upperThousandTimes = Decimal(100)
        for _ in range(times):
            print(_)
            upperThousandTimes = self.shortStrategy._getFollowingCheckpointPrice(upperThousandTimes)
        #print(upperThousandTimes)
        for _ in range(times):
            upperThousandTimes = self.shortStrategy._getPreviousCheckpointPrice(upperThousandTimes) 
        self.assertEqual(upperThousandTimes,Decimal(100))
    
    def test_calcular_saltos_en_progresion(self):
        rootCheckpoint = Decimal(self.shortStrategy.rootCheckpoint)
        print("rootCheckpoint:", rootCheckpoint)
        self.assertEqual(self.shortStrategy.calcular_saltos_en_progresion(rootCheckpoint,self.shortStrategy.getNthProgresionValueFromCheckpoint(5000,self.shortStrategy.rootCheckpoint)),-4999)
    
    def test_getMakerPrice(self):
        self.mock_interface.pricePrecision = 1
        self.assertEqual(self.shortStrategy.getMakerPrice(Decimal("0.5")),Decimal("0.6"))

        pass
    
    def test_getNthProgresionValueFromCheckpoint(self):
        self.assertEqual(self.shortStrategy.getNthProgresionValueFromCheckpoint(1,self.shortStrategy.rootCheckpoint),Decimal('99.90009990'))
        self.assertEqual(self.shortStrategy.getNthProgresionValueFromCheckpoint(2,self.shortStrategy.rootCheckpoint),Decimal('99.80029960'))
        self.assertEqual(self.shortStrategy.getNthProgresionValueFromCheckpoint(3,self.shortStrategy.rootCheckpoint),Decimal('99.70059900'))

    async def test_evaluar_precio(self):
        print("\n")
        self.mock_interface.pricePrecision = 8
        self.mock_interface.amountPrecision = 8
        self.mock_interface.notionalMin = 5 #required?
        self.mock_interface.saveStrategyState = Mock()
                        
        #orden de argumentos de putOrder:
        #position_side, order_side, amount, price, orderType
        
        precioEtapa = self.shortStrategy.lastCheckpoint
        print("\n\n##Etapa1 Evaluar precio##",precioEtapa)
        await self.shortStrategy.evaluar_precio(precioEtapa)
        self.shortStrategy.interface.putOrder.assert_not_called()

        precioEtapa = self.shortStrategy.getNthProgresionValueFromCheckpoint(1,self.shortStrategy.rootCheckpoint)
        print("\n\n##Etapa2 Evaluar precio##",precioEtapa)
        await self.shortStrategy.evaluar_precio(precioEtapa)
        self.shortStrategy.interface.putOrder.assert_not_called()

        precioEtapa = self.shortStrategy.getNthProgresionValueFromCheckpoint(2,self.shortStrategy.rootCheckpoint)
        print("\n\n##Etapa3 Evaluar precio##",precioEtapa)
        await self.shortStrategy.evaluar_precio(precioEtapa)

        self.shortStrategy.interface.putOrder.assert_called_with("short","sell",Decimal("0.05010005"),precioEtapa+Decimal("1e-{0}".format(self.shortStrategy.interface.pricePrecision)),"limit")
        # Verifica que se haya llamado a la función de orden correctamente
    
    
    
            
    def test_updateReferencePrice(self):
        self.mock_interface.pricePrecision = 8
        strategy = self.shortStrategy
        
        testNumber = 3
        currentCheckpoint = strategy.lastCheckpoint
        # strategy.lastCheckpoint, 
        # strategy.rootCheckpoint
        self.assertEqual(strategy.nextCheckpoint, Decimal("99.90009990"))

        self.assertEqual(strategy.previousCheckpoint, ((currentCheckpoint*(strategy.offset))).quantize(Decimal("1e-{}".format(strategy.interface.pricePrecision))))

        strategy.updatePriceCheckpoints(testNumber)
        self.assertEqual(strategy.lastCheckpoint, Decimal("100.30030010"))
        self.assertEqual(strategy.nextCheckpoint, Decimal('100.20010000'))
        self.assertEqual(strategy.previousCheckpoint, Decimal('100.40060040'))
    
class Test_StrategyA_isolated(IsolatedAsyncioTestCase):
        
    def test_calcular_saltos_en_progresion(self):
        print("\n Test test_calcular_saltos_en_progresion starts")
        mock_interface = MagicMock()
        mock_interface.pricePrecision = 8
        mock_interface.amountPrecision = 8
        mock_interface.notionalMin = 5
        
        data:StrategyStorage = {
            "positionSide": "short",
            "offset": "1.01",
            "rootCheckpoint":"100",
            "lastCheckpoint":"100",
            "profit_operations":[],
            "consecutives_price_fordward":0
        }
        shortStrategy = StrategyA(mock_interface, data)  # Crea una instancia de StrategyA


        currentCheckpoint = Decimal(shortStrategy.lastCheckpoint)
        priceList:list[float] = [99,100,98,100,99,98]
        for newPrice in priceList:
            if newPrice == priceList[0]:
                self.assertEqual(shortStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),-1)
            elif newPrice == priceList[1]:
                self.assertEqual(shortStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),0)
            elif newPrice == priceList[2]:
                self.assertEqual(shortStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),-2)
    
    async def test_evaluar_precio2(self):
        mock_interface = AsyncMock()
        mock_interface.pricePrecision = 8
        profitOperation:list[ProfitOperation]=[
            {
                "checkpoint":Decimal("100.20010000").quantize(Decimal("1e-{}".format(mock_interface.pricePrecision))),
                "openingOrderId":"1",
                "closingOrderId":None
            },
            {
                "checkpoint":Decimal("100.30030010").quantize(Decimal("1e-{}".format(mock_interface.pricePrecision))),
                "openingOrderId":"2",
                "closingOrderId":None
            }
        ]
        data:StrategyStorage = {
            "positionSide": "short",
            "offset": "1.01",
            "rootCheckpoint":"100",
            "lastCheckpoint":"100",
            "profit_operations":[*profitOperation],
            "consecutives_price_fordward":0
        }
        
        putOrder = AsyncMock()
        putOrder.side_effect = [{"info":{"clientOrderId":"3"}},{"info":{"clientOrderId":"4"}},{"info":{"clientOrderId":"5"}},{"info":{"clientOrderId":"6"}},{"info":{"clientOrderId":"7"}},{"info":{"clientOrderId":"8"}}]
        mock_interface.amountPrecision = 8
        mock_interface.notionalMin = 5
        mock_interface.putOrder = putOrder
        mock_interface.strategyData = data
        mock_interface.saveStrategyState = Mock()
        async def fetch_order(clientOrderId):
            print("fetching clientOrderId", clientOrderId)
            if clientOrderId == "1":
                return {"status":"closed"}
            elif clientOrderId == "2":
                return {"status":"open"}
            elif clientOrderId == "3":
                return {"status":"open"}
            else:
                raise Exception(f"No more Mocks ClientOrderId({clientOrderId}) (type:{type(clientOrderId)})")
        mock_interface.fetch_order = fetch_order 
        
        

        shortStrategy = StrategyA(mock_interface, data)  # Crea una instancia de StrategyA
           
        priceList:list[float] = [100,99,98,100,99,98,97]

        for newPrice in priceList:
            await shortStrategy.evaluar_precio(Decimal(str(newPrice)))
        putOrder.assert_called()
        self.assertEqual(putOrder.call_count,2)

            

    