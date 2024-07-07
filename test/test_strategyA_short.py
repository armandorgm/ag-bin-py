import json
from pprint import pprint
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
        self.assertEqual(self.shortStrategy.calcular_saltos_en_progresion(rootCheckpoint,self.shortStrategy.getNthProgresionValueFromCheckpoint(5000,self.shortStrategy.rootCheckpoint)),4999)
    
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

        print(f"\nlastCheckpoint before update ({strategy.lastCheckpoint})")
        strategy.updateLastCheckpoint(testNumber)
        #self.assertEqual(strategy.lastCheckpoint, Decimal("99."))
        self.assertEqual(strategy.lastCheckpoint, Decimal("99.70059900"))
        self.assertEqual(strategy.nextCheckpoint, Decimal('99.60099800'))
        self.assertEqual(strategy.previousCheckpoint, Decimal('99.80029960'))
    
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
                #self.assertEqual(shortStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),-1)
                self.assertEqual(shortStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),1)
            elif newPrice == priceList[1]:
                self.assertEqual(shortStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),0)
            elif newPrice == priceList[2]:
                #self.assertEqual(shortStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),-2)
                self.assertEqual(shortStrategy.calcular_saltos_en_progresion(currentCheckpoint, Decimal(str(newPrice))),2)
    
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

class Test_Short2(IsolatedAsyncioTestCase):
    def setUp(self):
        self.pendingOperations='[{"checkpoint": "0.09980", "openingOrderId": "c305fbad-de52-47bd-bbca-425a3da54eca", "closingOrderId": null}, {"checkpoint": "0.09960", "openingOrderId": "9f94139f-6fcf-4c82-9dc3-afbd61d7a0e9", "closingOrderId": null}, {"checkpoint": "0.09960", "openingOrderId": "611f8b1e-ba53-49dd-94ca-8f7af1652c05", "closingOrderId": null}, {"checkpoint": "0.09940", "openingOrderId": "353f95ea-8770-4006-b41f-9e85345ce8b3", "closingOrderId": null}, {"checkpoint": "0.09920", "openingOrderId": "11495006-6c2b-4a9c-8ada-f494a9f8916a", "closingOrderId": null}, {"checkpoint": "0.09940", "openingOrderId": "8e0c4e51-9534-46d3-9620-7211441f2bb1", "closingOrderId": null}, {"checkpoint": "0.09920", "openingOrderId": "dda58b92-297c-432e-a815-4dccf362212b", "closingOrderId": null}, {"checkpoint": "0.09940", "openingOrderId": "6f56fe68-4b53-4d03-ab1c-8c2c020275e9", "closingOrderId": null}, {"checkpoint": "0.09900", "openingOrderId": "272d333f-22a8-4f62-ae6b-2df761f7c438", "closingOrderId": null}, {"checkpoint": "0.09880", "openingOrderId": "5175b192-24d1-4450-816f-c75edd15b197", "closingOrderId": null}, {"checkpoint": "0.09860", "openingOrderId": "4e232709-1d7e-4245-8b10-595b2b53aae7", "closingOrderId": null}, {"checkpoint": "0.09840", "openingOrderId": "cab689b6-2f8a-49b8-95cf-8e96f3e62763", "closingOrderId": null}, {"checkpoint": "0.09820", "openingOrderId": "2b244699-d8e4-4889-b0a5-70871d43ef03", "closingOrderId": null}, {"checkpoint": "0.09800", "openingOrderId": "2c9e1b25-5c7c-4f9d-87b7-3fe8723a892f", "closingOrderId": null}, {"checkpoint": "0.09780", "openingOrderId": "9ad7ae43-8bd7-4b6a-aea7-059d98259e2d", "closingOrderId": null}, {"checkpoint": "0.09760", "openingOrderId": "f1a6e5eb-dbfe-4254-b0b3-b7b6acfdf7a5", "closingOrderId": null}, {"checkpoint": "0.09741", "openingOrderId": "522b5002-2f1c-4c3a-a934-69a7f264faae", "closingOrderId": null}, {"checkpoint": "0.09683", "openingOrderId": "03fc8414-25fc-4640-ab54-87be6ab5ff7c", "closingOrderId": null}, {"checkpoint": "0.09664", "openingOrderId": "bc33beb7-2c7c-4f45-888c-cb32dbe7f8a5", "closingOrderId": null}, {"checkpoint": "0.09645", "openingOrderId": "276ac517-0559-4477-b3fe-52bed50b92e7", "closingOrderId": null}, {"checkpoint": "0.09606", "openingOrderId": "d0cdc170-8af1-4af1-b602-2e0daff37604", "closingOrderId": null}, {"checkpoint": "0.09568", "openingOrderId": "e3c95711-caf2-49f1-a38b-2bb38626021e", "closingOrderId": null}, {"checkpoint": "0.09511", "openingOrderId": "81a75f27-c614-4943-814e-884c60e40e2e", "closingOrderId": null}, {"checkpoint": "0.09473", "openingOrderId": "58c4a5fa-d2b6-4a62-9d8b-0eb0ac88470f", "closingOrderId": null}, {"checkpoint": "0.09435", "openingOrderId": "1a15d91c-1c7b-4b16-9d39-339298cdcb41", "closingOrderId": null}, {"checkpoint": "0.09568", "openingOrderId": "6bb90d74-0201-4437-a7d9-dca7762b897a", "closingOrderId": null}, {"checkpoint": "0.09549", "openingOrderId": "763953c4-2776-47f7-af5a-eedf73ab4441", "closingOrderId": null}, {"checkpoint": "0.09511", "openingOrderId": "a77a3706-888e-4c9f-8a78-bcd4c807c749", "closingOrderId": null}, {"checkpoint": "0.09492", "openingOrderId": "1dd77eaf-470c-4584-b01d-4704fb46c25f", "closingOrderId": null}, {"checkpoint": "0.09473", "openingOrderId": "3a37a7e0-0125-4a6e-94e8-83c36d276b34", "closingOrderId": null}, {"checkpoint": "0.09304", "openingOrderId": "3a1230f7-5698-41a0-ae85-15a57cd52f25", "closingOrderId": null}, {"checkpoint": "0.09549", "openingOrderId": "cb0be68b-0c82-4997-859e-ce9f0fce6740", "closingOrderId": null}, {"checkpoint": "0.09530", "openingOrderId": "545d9380-882b-4cd8-9591-75e553a09639", "closingOrderId": null}, {"checkpoint": "0.09530", "openingOrderId": "335b665f-6586-4891-9a95-f3c5a01b5374", "closingOrderId": null}, {"checkpoint": "0.09511", "openingOrderId": "47cf0162-e3a4-43f9-acd5-917080100c49", "closingOrderId": null}, {"checkpoint": "0.09511", "openingOrderId": "741be892-0343-4774-a021-a3751be5902e", "closingOrderId": null}, {"checkpoint": "0.09492", "openingOrderId": "3cb8e39e-0fcd-44d8-874a-6ae530ca2247", "closingOrderId": null}, {"checkpoint": "0.09473", "openingOrderId": "8e273ecb-b5dd-4f33-a82c-7bc1df94dd88", "closingOrderId": null}, {"checkpoint": "0.09454", "openingOrderId": "c4073645-19c2-48f2-a8a1-bb65adc0a63c", "closingOrderId": null}, {"checkpoint": "0.09435", "openingOrderId": "89fbb01f-1f64-4449-a3e9-6ae7364daf68", "closingOrderId": null}, {"checkpoint": "0.09416", "openingOrderId": "76adceb6-54ee-4eeb-a2d1-02283816f9cf", "closingOrderId": null}]'
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
            "profit_operations":json.loads(self.pendingOperations)
        }
        self.shortStrategy = StrategyA(self.mock_interface, dataStorage)  # Crea una instancia de StrategyA

    async def test_preStart(self):
        pprint(self.shortStrategy._profitOperations)
        await self.shortStrategy.preInit(Mock())
        self.assertEqual(self.shortStrategy._profitOperations,1)