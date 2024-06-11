from dao import OrderManagerDAO
from  ccxt.pro import binanceusdm
from pprint import pprint
import logging
from sql_models.models import BotOperation_model
from db_integrity import DbIntegrity
from interfaces.iOrderManager import iBotManager
from bot_operation import Bot_Operation

# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('output.log'),  # Archivo de salida
                        logging.StreamHandler()  # Salida de consola
                    ])
logger = logging.getLogger(__name__)

class OrderMonitor:
        def __init__(self, orderManager:"iBotManager",exchange:binanceusdm,dao:OrderManagerDAO):
            self.orderManager = orderManager
            self.orderContainer =[]
            self.exchange = exchange
            self.dao = dao
            self.active = True
            self.integrityChecker = DbIntegrity(dao,exchange)
        
        
        def find_enclosing_thresholds(self, entry_price, current_price, threshold):
            # Determinar si se debe incrementar o disminuir el precio
            step_function = (lambda x: x * (1 + (threshold / 100))) if current_price > entry_price else (lambda x: x / (1 + (threshold / 100)))
            
            nearer_threshold = entry_price
            farther_threshold = step_function(entry_price)
            
            # Iterar para encontrar los umbrales más cercanos
            while (current_price > entry_price and nearer_threshold < current_price) or (current_price < entry_price and nearer_threshold > current_price):
                if (current_price > entry_price and farther_threshold >= current_price) or (current_price < entry_price and farther_threshold <= current_price):
                    break
                nearer_threshold = farther_threshold
                farther_threshold = step_function(farther_threshold)
            
            # Asegurar que los umbrales estén en el orden correcto
            lower_threshold = min(nearer_threshold, farther_threshold)
            upper_threshold = max(nearer_threshold, farther_threshold)
            
            return lower_threshold, upper_threshold
    
        async def calcular_escala_exponencial(self,botOperationId:int):
            botOperation = self.dao.getBotOperation(botOperationId)
            # Calculamos la relación entre el precio actual y el precio de entrada
            currentPrice = (await self.exchange.watch_ticker(botOperation.symbol))['last']
            relacion = currentPrice / botOperation.entry_price
            # Determinamos la escala exponencial (por ejemplo, 1.1 para un incremento del 10%)
            escala_actual = relacion ** (1 / 2)  # num_escalas es el número de escalas consecutivas
            return escala_actual
        
        def is_within_threshold(slotPrice, currentPrice, threshold):
            threshold_amount = slotPrice * (threshold / 100)
            return abs(slotPrice - currentPrice) <= threshold_amount
        
        
                       
        async def start(self):
            botOperations = self.dao.getBotOperations()
            for botOperation in botOperations:
                theBotOperation = Bot_Operation(botOperation.id,botOperation.entry_price,botOperation.position_side,botOperation.symbol,botOperation.threshold,"standard")
                print(f"\n{'#'*4} botOperation {botOperation.id} {botOperation.symbol} {botOperation.position_side} {'#'*4}")
                await self.orderManager.clearProfitOperationByBotOperationId(botOperation.id)
                
                
                currentPrice = (await self.exchange.watch_ticker(botOperation.symbol))['last']
                
                lowerPricethreshold,upperPricethreshold = self.find_enclosing_thresholds(botOperation.entry_price, currentPrice,botOperation.threshold)
                slots = [lowerPricethreshold,upperPricethreshold]
                print(botOperation.position_side.lower(),"== long ->", botOperation.position_side.lower() == "long")
                
                if botOperation.position_side.lower() == "long":
                    slots.reverse()
                    print("slots inveridos para colocar primero la orden mas lejana ")
                    
                for slotPrice in slots:
                    slotPrice = float(self.exchange.price_to_precision(botOperation.symbol, slotPrice))

                    print("checking slot price",slotPrice)
                    if( await self.orderManager.isSlotInactive(botOperation.id, slotPrice) ):
                        print(f"slot {slotPrice} for {botOperation.symbol} is open")
                        await self.orderManager.create_profit_operation(botOperation.id,slotPrice)

                    
                    
                    
            