import json
import unittest
from unittest.mock import patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cleanroot.clean.bot_strategies.strategy_a.strategyA_dao import StrategyA_DAO


class TestStrategyA_DAO(unittest.TestCase):
    def setUp(self):
        # Configura una instancia de StrategyA_DAO con un archivo de base de datos de prueba
        #self.dao = StrategyA_DAO("test/test.db")
        self.dao = StrategyA_DAO(":memory:")

    def test_set_get_pending_operations(self):
        pending_operations = self.dao.create_pending_operations("101101",10,"long",100.00, {'dada':'dodo'},101.00)
        pending_operations = self.dao.get_pending_operations()
        self.assertEqual(pending_operations[0].id,1)
        self.assertEqual((pending_operations[0].exchangeId),"101101")
        self.assertEqual((pending_operations[0].amount),10)
        self.assertEqual((pending_operations[0].position_side),"long")
        self.assertEqual((pending_operations[0].open_price),100.00)
        self.assertEqual((pending_operations[0].open_fee),json.loads('{"dada":"dodo"}'))
        self.assertEqual((pending_operations[0].close_price),101.00)
        self.assertEqual((pending_operations[0].close_fee),None)
        
        self.assertIsInstance(pending_operations, list)
        self.assertIsInstance((pending_operations[0].id),int)
        self.assertIsInstance((pending_operations[0].amount),float)
        self.assertIsInstance((pending_operations[0].position_side),str)
        self.assertIsInstance((pending_operations[0].open_price),float)
        self.assertIsInstance((pending_operations[0].open_fee),float)
        self.assertIsInstance((pending_operations[0].close_price),float)
        self.assertIsInstance((pending_operations[0].close_fee),float|None)

        