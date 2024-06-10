import asyncio
from config_manager import ConfigManager
from bot_manager import OrderManager
from user_interface import UserInterface


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
        order_manager = OrderManager(api_key, secret, user_interface,testMode)
        try:
            await order_manager.theTime()
            await order_manager.startMenu()
        except KeyboardInterrupt:
            await order_manager.exchange.close()
    
if __name__ == '__main__':
        asyncio.run(main())
    