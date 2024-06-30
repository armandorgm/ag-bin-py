from decimal import Decimal
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock
from cleanroot.clean.bot_operation import Bot_Operation


class Test_Bot_Operation(unittest.IsolatedAsyncioTestCase):
  def setUp(self):
    # Configura una instancia de StrategyA_DAO con un archivo de base de datos de prueba
    #self.dao = StrategyA_DAO("test/test.db")
    mockExchange = AsyncMock()
    
    botStrategyConfig = MagicMock()
    botStrategyConfig.strategy_id = 1
    botStrategyConfig.data = '{"a":1,"c":3,"b":"jamon"}'
    
    mockDao = MagicMock()
    mockDao.getBotStrategyConfig.return_value = botStrategyConfig
    
    mockStrategy = MagicMock()
    mockStrategy.strategy_id = 1
    mockStrategy.id = 1

    self.bo = Bot_Operation(1,mockExchange,mockDao,"SYMBOL",[mockStrategy],1)
    
  async def test_putOrder(self):
    await self.bo.putOrder("long","buy",Decimal(250),Decimal(500),"limit")