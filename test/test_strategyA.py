from unittest import IsolatedAsyncioTestCase,TestCase,skip
from unittest.mock import MagicMock
from cleanroot.clean.bot_strategies.strategy_a.strategyA import StrategyA
from decimal import Decimal,getcontext

import pytest
context = getcontext()
context.prec = 16
class TestStrategyA(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_interface = MagicMock()
        self.offset = Decimal(str(100/100))
        self.initialReferenceCheckpoint=Decimal("1")
        
        positionSide1 = "long"
        self.longStrategy = StrategyA(self.mock_interface, positionSide1, self.offset,self.initialReferenceCheckpoint)  # Crea una instancia de StrategyA
    
        
        positionSide2 = "short"
        self.shortStrategy = StrategyA(self.mock_interface, positionSide2, self.offset,self.initialReferenceCheckpoint)  # Crea una instancia de StrategyA

    
    #@skip("Esta prueba está deshabilitada temporalmente")
    def test_ref_price_initialization(self):

        precision = Decimal("0.00000001")
        # Verifica que la referencia de precio se inicialice correctamente
        self.assertEqual(self.longStrategy.reference_price, self.initialReferenceCheckpoint)
        self.assertEqual(self.longStrategy.nextPrice, Decimal((self.longStrategy.offset+1)*self.longStrategy.reference_price))
        self.assertEqual(self.longStrategy.previousPrice.quantize(precision), Decimal(self.longStrategy.reference_price/(self.longStrategy.offset+1))) # type: ignore
    
    
    def test_backAndFordwardCheckpoints(self):
        times = 5000
        upperThousandTimes = Decimal(100)
        for _ in range(times):
            upperThousandTimes = self.longStrategy.getFollowingCheckpointPrice(upperThousandTimes)
        #print(upperThousandTimes)
        for _ in range(times):
            upperThousandTimes = self.longStrategy.getPreviousCheckpointPrice(upperThousandTimes) 
        self.assertEqual(upperThousandTimes,Decimal(100))
    
    
    def getProgresionValueFromCurrentPriceRef(self,numero_de_saltos_de_la_progresion:int):
        try:
            value = self.longStrategy.reference_price*(1+self.longStrategy.offset)**numero_de_saltos_de_la_progresion
            return value
        except Exception as e:
            print("getProgresionValueFromCurrentPriceRef():", e)
            raise e
    
    def test_calcular_saltos_en_progresion(self):
        currentCheckpoint = Decimal(self.longStrategy.reference_price)
        
        self.assertEqual(self.longStrategy.calcular_saltos_en_progresion(currentCheckpoint, currentCheckpoint),0)
        rango_de_error = []
        lastError = None
        for i in range(5000):
            j = i-2500
            try:
                if self.getProgresionValueFromCurrentPriceRef(j) != float("inf"):
                    self.assertEqual(self.longStrategy.calcular_saltos_en_progresion(currentCheckpoint,self.getProgresionValueFromCurrentPriceRef(j)),j)
                    if len(rango_de_error) == 1:
                        rango_de_error.append(j-1)
            #except ValueError as e:
            #    print(e)
            except Exception as e:
                if lastError != str(e):
                    lastError = str(e)
                    print(f"\n###### ERROR({e}) a partir de ({j}) ######")
                if len(rango_de_error) == 0:
                    rango_de_error.append(j)
                raise e
        print("rango_de_error",rango_de_error[0],rango_de_error[1])
    
    def test_getMakerPrice(self):
        self.mock_interface.pricePrecision = 1
        self.assertEqual(self.longStrategy.getMakerPrice(Decimal("0.5")),Decimal("0.4"))
        self.assertEqual(self.shortStrategy.getMakerPrice(Decimal("0.5")),Decimal("0.6"))

        pass
    
    @pytest.mark.asyncio
    async def test_evaluar_precio(self):
            
        #self.mock_interface.tick =Decimal(0.1)
        self.mock_interface.pricePrecision = 0
        #self.mock_interface.get_min_amount.return_value = Decimal("0.00000001")
        self.mock_interface.amountPrecision = 8
        self.mock_interface.notionalMin = 5
        
            
        newPrice = Decimal(109)

                
        # Ejecuta la evaluación de precio
        #orden de argumentos de putOrder:
        #position_side, order_side, amount, price, orderType

        await self.longStrategy.evaluar_precio(self.longStrategy.reference_price)
        self.longStrategy.interface.putOrder.assert_not_called()

        print("##1##",self.getProgresionValueFromCurrentPriceRef(1))
        await self.longStrategy.evaluar_precio(self.getProgresionValueFromCurrentPriceRef(1))
        self.longStrategy.interface.putOrder.assert_not_called()

        
        print("##2##",self.getProgresionValueFromCurrentPriceRef(1))
        await self.longStrategy.evaluar_precio(self.getProgresionValueFromCurrentPriceRef(1))

        self.longStrategy.interface.putOrder.assert_called_with("long","buy",Decimal("1.66666667"),Decimal(3),"limit")
        # Verifica que se haya llamado a la función de orden correctamente
    
    def test_updateReferencePrice(self):
        testNumber = 3
        strategy = self.longStrategy
        currentCheckpoint = strategy.reference_price
        self.assertEqual(strategy.reference_price, strategy.bornPrice)
        self.assertEqual(strategy.nextPrice, currentCheckpoint*(1+strategy.offset))
        self.assertEqual(strategy.previousPrice, currentCheckpoint/(1+strategy.offset))

        strategy.updatePriceCheckpoints(testNumber)
        self.assertEqual(strategy.reference_price, currentCheckpoint*((1+strategy.offset)**testNumber))
        self.assertEqual(strategy.nextPrice, currentCheckpoint*((1+strategy.offset)**(testNumber+1)))
        self.assertEqual(strategy.previousPrice, currentCheckpoint*((1+strategy.offset)**(testNumber-1)))
    
