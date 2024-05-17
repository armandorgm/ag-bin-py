import subprocess
import sys

def open_new_console(script_path:str, order_id:str,symbol:str,type:str,side:str,amount:str,price:str, positionSide:str):
    subprocess.Popen(
        [sys.executable, script_path, order_id, symbol,type,side,amount,price, positionSide],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )


if __name__ == "__main__":
    # These values are just placeholders; you would pass the actual values.
    open_new_console(
        'c:/Users/arman/myProjects/ag-bin-py/my_binance_wrapper.py',  # Script path
        '55910880457',                                                # Order ID
        'BNBUSDT',                                                    # Symbol
        'MARKET',                                                     # Order type
        'BUY',                                                        # Side
        '1.23',                                                       # Amount (placeholder value)
        '0',                                                          # Price (placeholder value, can be ignored for market orders)
        'LONG'                                                        # Position Side
    )