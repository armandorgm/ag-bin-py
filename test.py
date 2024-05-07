import ccxt
from dotenv import load_dotenv
import os


# Imprime una lista de todas las clases de intercambio disponibles
def main():
    load_dotenv("secrets.env")

    print(os.getenv("API_KEY"))
    print(ccxt.exchanges)

main()