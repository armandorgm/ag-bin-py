import asyncio
from config_manager import ConfigManager
from order_manager import OrderManager
from user_interface import UserInterface


async def main():
    config_manager = ConfigManager()
    #######
    testMode = False
    #######
    selection = input('''
1.) testMode
2.)Realmode          ''')
    match(selection):
        case "1":
            api_key, secret = config_manager.get_api_test_credentials()
            testMode = True
        case "2":
            api_key, secret = config_manager.get_api_credentials()
    user_interface = UserInterface(["BNB/USDT", "ATA/USDT", "TRX/USDT","BTC/USDT"])
    order_manager = OrderManager(api_key, secret, user_interface,testMode)
    await order_manager.startMenu()
    
    
if __name__ == '__main__':
        asyncio.run(main())
    