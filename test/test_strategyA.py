import random
import unittest
from unittest.mock import MagicMock, Mock,create_autospec
from cleanroot.clean.bot_strategies.strategy_a.strategyA import StrategyA
from decimal import Decimal,getcontext
from cleanroot.clean.interfaces.exchange_basic import SymbolPrecision
from cleanroot.clean.bot_strategies.profit_operation import Profit_Operation
from cleanroot.clean.interfaces.types import Order
context = getcontext()
context.prec = 16

class TestStrategyA(unittest.TestCase):
    def setUp(self):
        # Configura cualquier inicialización necesaria aquí
        mock_dao = MagicMock()
        
        precision:SymbolPrecision = {'amount': 3, 'base': 8, 'price': 1, 'quote': 8}
        self.strategy = StrategyA(precision,Decimal(str(0.1/100)),Decimal("100"),mock_dao)  # Crea una instancia de StrategyA

    def test_ref_price_initialization(self):
        precision = Decimal("0.00000001")
        # Verifica que la referencia de precio se inicialice correctamente
        self.assertEqual(self.strategy.reference_price, Decimal("100"))
        self.assertEqual(self.strategy.nextPrice, Decimal("100.1"))
        self.assertEqual(self.strategy.previousPrice.quantize(precision), Decimal("99.90009990")) # type: ignore
    
    def test_backAndFordwardCheckpoints(self):
        times = 5000
        upperThousandTimes = Decimal(100)
        for _ in range(times):
            upperThousandTimes = self.strategy.getFollowingCheckpointPrice(upperThousandTimes)
        #print(upperThousandTimes)
        for _ in range(times):
            upperThousandTimes = self.strategy.getPreviousCheckpointPrice(upperThousandTimes) 
        self.assertEqual(upperThousandTimes,Decimal(100))
    
    def test_getNextGeometricBound(self):
        progresion:list[str]= [100] # type: ignore
        for _ in range(10):
            progresion.append(str(self.strategy.getFollowingCheckpointPrice(Decimal(progresion[-1]))))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal("100.01")),Decimal("100.1"))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal("100.1")),Decimal("100.200100"))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal("100.1")),Decimal("100.200100"))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal(progresion[2])),Decimal(progresion[3]))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal(progresion[3])),Decimal(progresion[4]))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal(progresion[4])),Decimal(progresion[5]))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal(progresion[5])),Decimal(progresion[6]))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal(progresion[6])),Decimal(progresion[7]))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal(progresion[7])),Decimal(progresion[8]))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal(progresion[8])),Decimal(progresion[9]))

        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal("99.99")),Decimal(100))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal("99.90")),Decimal("99.90009990009990"))
        self.assertEqual(self.strategy.getNextGeometricBound(Decimal(100),Decimal("99.8001")),Decimal("99.80029960049940"))
    
    def test_calcular_saltos_en_progresion(self):
        print("offset is:",self.strategy.offset)
        self.assertEqual(self.strategy.calcular_saltos_en_progresion(Decimal(100),Decimal("100.1")),1)
        self.assertEqual(self.strategy.calcular_saltos_en_progresion(Decimal(100),Decimal("14804.28361626417")),5000)
        self.assertEqual(self.strategy.calcular_saltos_en_progresion(Decimal("14804.28361626417"),Decimal(100)),-5000)
    
    def test_evaluar_precio(self):
        # Crea datos de mercado ficticios
        def create_order_response():
            return {
            "id":random.randint(10**15, (10**16)-1),
            "amount":45,
            "average":0.12000,
            "fee":1,
            "info":{"positionSide":"LONG"}}
        orderResponse = create_order_response()
        
        # Crea un mock para la función de orden
        orden_callback = Mock()            
        orden_callback.return_value = orderResponse
        
        
        #Emula el metodo dao.create_pending_operations()
        profit_operation_instance_mock:Profit_Operation = create_autospec(Profit_Operation)
        profit_operation_instance_mock.position_side = orderResponse["info"]["positionSide"]
        profit_operation_instance_mock.amount =orderResponse["amount"]
        profit_operation_instance_mock.close_price =self.strategy.getProfitPriceOf(orderResponse["amount"])
        self.strategy.dao.create_pending_operations.return_value = profit_operation_instance_mock
            
        # Ejecuta la evaluación de precio
        self.strategy.evaluar_precio(Decimal(100), orden_callback)
        orden_callback.assert_not_called()

        self.strategy.evaluar_precio(Decimal(107), orden_callback)
        orden_callback.assert_not_called()


        self.strategy.evaluar_precio(Decimal(109), orden_callback)
        self.strategy.dao.create_pending_operations.assert_called_with("Banana")
        # Verifica que se haya llamado a la función de orden correctamente
        orden_callback.assert_called_with("LONG", "buy", 43, 110.09)
    
    """
    def test_updateReferencePrice(self):
        self.strategy.updatePriceCheckpoints(Decimal("100.100001"),"price_moved_up")
        self.assertEqual(self.strategy.reference_price, Decimal("100.11"))
        self.assertEqual(self.strategy.nextPrice, Decimal("100.1"))
        self.assertEqual(self.strategy.previousPrice, Decimal("100.20010"))
    

    

        
    def test_get_min_amount(self):
        # Verifica que el valor mínimo de cantidad sea correcto
        self.assertEqual(self.strategy.get_min_amount(), 43)
    
    def test_evaluar_precio__1(self):
        # Crea un mock para la función de orden
        orden_callback = Mock()
        orden_callback.return_value = {"id" :"1","amount":1,"average": 7, "fee":{"foo":"foo"}}
        
        # Ejecuta la evaluación de precio
        self.strategy.evaluar_precio(100, orden_callback)
        self.strategy.evaluar_precio(101, orden_callback)

        
        orden_callback.assert_called_with("PAPA")
    """
   

    """
    def test_evaluar_precio2(self):
        # Crea datos de mercado ficticios
        datos_mercado = {"precio_actual": 105}

        # Crea un mock para la función de orden
        orden_callback = Mock()

        # Ejecuta la evaluación de precio
        self.strategy.evaluar_precio(datos_mercado, orden_callback)

        datos_mercado = {"precio_actual": 103}
        self.strategy.evaluar_precio(datos_mercado, orden_callback)

        datos_mercado = {"precio_actual": 101}
        self.strategy.evaluar_precio(datos_mercado, orden_callback)

        # Verifica que se haya llamado a la función de orden correctamente
        orden_callback.assert_called_with("SHORT", "sell", 43, 110.09)
    """    
        
    """
    def test_get_pending_operations(self):
        pending_operations = self.strategy.pending_operations
        self.assertIsInstance(pending_operations, list)
        #self.assertEqual()
"""
        