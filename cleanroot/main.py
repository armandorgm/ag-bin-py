print("__name__:",__name__)
print("__package__:",__package__)
import asyncio
from clean.config_manager import ConfigManager
from clean.bot_manager import BotManager
from clean.user_interface import UserInterface


async def main():
    config_manager = ConfigManager()
    #######
    testMode = False
    #######
    selection = input('''
1.) testMode
2.) Realmode          ''')
    match(selection):
        case "1":
            api_key, secret = config_manager.get_api_test_credentials()
            testMode = True
        case "2":
            api_key, secret = config_manager.get_api_credentials()
        case _:
            pass
    if api_key and secret:
        user_interface = UserInterface(["BNB/USDT", "ATA/USDT", "TRX/USDT","BTC/USDT"])
        order_manager = BotManager(api_key, secret, user_interface,testMode)
        try:
            await order_manager.theTime()
            await order_manager.startMenu()
        except KeyboardInterrupt:
            pass
        finally:
            await order_manager.exchange.close()
    
if __name__ == '__main__':
    asyncio.run(main())
    