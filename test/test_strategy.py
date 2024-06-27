from decimal import Decimal
from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock
from cleanroot.clean.bot_strategies.strategy import Strategy

class FooStrategy(Strategy):
    def saveState(self):
        pass
    def evaluar_precio(self, datos_mercado: Decimal) -> Any:
        pass
    
class Test_Strategy(TestCase):
    def setUp(self):
        self.mock_interface = MagicMock()
        self.strategy = FooStrategy(self.mock_interface)
    
    def test_get_min_amount(self,):
        self.mock_interface.amountPrecision = 8
        self.mock_interface.notionalMin = 33555
        
        price = Decimal(100)
        self.assertEqual(float(self.strategy.get_min_amount(price)),335.55)
        
    def test_get_min_amount2(self,):
        self.mock_interface.amountPrecision = 1
        self.mock_interface.notionalMin = 33555
        
        price = Decimal(100)
        self.assertEqual(float(self.strategy.get_min_amount(price)),335.6)
    