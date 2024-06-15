import unittest
from unittest.mock import patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from clean.bot_strategies.strategy_a.strategyA_dao import StrategyA_DAO, Pending_Operation_Model, Reference_Price_Model


class TestStrategyA_DAO(unittest.TestCase):
    def setUp(self):
        # Configura una instancia de StrategyA_DAO con un archivo de base de datos de prueba
        self.dao = StrategyA_DAO("test/test.db")

    def test_get_pending_operations(self):
        # Prueba el método get_pending_operations
        pending_operations = self.dao.get_pending_operations()
        self.assertIsInstance(pending_operations, list)
        self.assertIsInstance((pending_operations[0].id),int)
        self.assertIsInstance((pending_operations[0].amount),float)
        self.assertIsInstance((pending_operations[0].close_fee),float)
        self.assertIsInstance((pending_operations[0].position_side),str)
        self.assertIsInstance((pending_operations[0].closing_price),float)
        self.assertIsInstance((pending_operations[0].open_fee),float)
    
    def test_get_reference_price(self):
        # Prueba el método get_reference_price
        reference_price = self.dao.get_reference_price(id=1)  # Cambia el ID según tus datos
        self.assertIsInstance(reference_price, (float, type(None)))
        # Agrega más aserciones específicas según tus necesidades