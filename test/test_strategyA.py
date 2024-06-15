import unittest
from unittest.mock import Mock
from clean.bot_strategies.strategy_a.main import StrategyA


class TestStrategyA(unittest.TestCase):
    def setUp(self):
        # Configura cualquier inicialización necesaria aquí
        self.strategy = StrategyA(1,offset=1)  # Crea una instancia de StrategyA

    def test_ref_price_initialization(self):
        # Verifica que la referencia de precio se inicialice correctamente
        self.assertIsNone(self.strategy.reference_price)
    
    def test_upper_and_lower_prices(self):
        # Establece una referencia de precio
        self.strategy.reference_price = 100

        # Verifica que los precios superior e inferior se calculen correctamente
        self.assertEqual(self.strategy.upper_price, 101)
        self.assertEqual(self.strategy.lower_price, 99)
        
    def test_get_min_amount(self):
        # Verifica que el valor mínimo de cantidad sea correcto
        self.assertEqual(self.strategy.get_min_amount(), 43)
    
    def test_evaluar_precio__1(self):
        # Crea datos de mercado ficticios
        datos_mercado = {"precio_actual": 105}

        # Crea un mock para la función de orden
        orden_callback = Mock()

        # Ejecuta la evaluación de precio
        self.strategy.evaluar_precio(datos_mercado, orden_callback)
    """
    def test_evaluar_precio(self):
        # Crea datos de mercado ficticios
        datos_mercado = {"precio_actual": 105}

        # Crea un mock para la función de orden
        orden_callback = Mock()

        # Ejecuta la evaluación de precio
        self.strategy.evaluar_precio(datos_mercado, orden_callback)

        datos_mercado = {"precio_actual": 107}
        self.strategy.evaluar_precio(datos_mercado, orden_callback)

        datos_mercado = {"precio_actual": 109}
        self.strategy.evaluar_precio(datos_mercado, orden_callback)

        # Verifica que se haya llamado a la función de orden correctamente
        orden_callback.assert_called_with("LONG", "buy", 43, 110.09)
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
        