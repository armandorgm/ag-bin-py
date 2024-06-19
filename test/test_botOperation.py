import unittest
from unittest.mock import Mock
from cleanroot.clean.bot_operation import Bot_Operation


class TestStrategyA(unittest.TestCase):
      def setUp(self):
        # Configura una instancia de StrategyA_DAO con un archivo de base de datos de prueba
        #self.dao = StrategyA_DAO("test/test.db")
        self.bo = Bot_Operation()