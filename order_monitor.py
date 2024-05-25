from dao import OrderManagerDAO
from  ccxt.pro import binanceusdm
from pprint import pprint
import logging
from models import BotOperation
from db_integrity import DbIntegrity
from interfaces.iOrderManager import iOrderManager

# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('output.log'),  # Archivo de salida
                        logging.StreamHandler()  # Salida de consola
                    ])
logger = logging.getLogger(__name__)

class OrderMonitor:
        def __init__(self, orderManager:"iOrderManager",exchange:binanceusdm,dao:OrderManagerDAO):
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
        
        async def isSlotInactive(self, botOperationId, slotPrice):
            botOperation = self.dao.getBotOperation(botOperationId)
            slotPrice = self.exchange.price_to_precision(botOperation.symbol, slotPrice)
            #slotList = self.dao.getProfitOperations()
            slotList = self.dao.getProfitOperationsByOperationId(botOperationId)
            print("slotList Lengh", len(slotList))
  
            for slot in slotList:
                if(str(slotPrice) == str(slot.slot_price)):
                    symbol = botOperation.symbol
                    print("price slot found")
                    openCloseOrderPairId = [slot.open_order_id, slot.take_profit_order_id]
                    for orderId in openCloseOrderPairId:
                        
                        if(orderId):
                            print("orderID found",orderId)
                            orderStatus = (await self.exchange.fetch_order(orderId, symbol))["status"]
                            if(orderStatus == "open"):
                                print(f"Order {orderId} is still active ({orderStatus})")
                                return False
                   
            return True
                       
        async def start(self):
            while self.active:
                botOperations = self.dao.getBotOperations()
                for botOperation in botOperations:
                    
                    currentPrice = (await self.exchange.watch_ticker(botOperation.symbol))['last']
                    
                    lowerPricethreshold,upperPricethreshold = self.find_enclosing_thresholds(botOperation.entry_price, currentPrice,botOperation.threshold)
                    slots = [lowerPricethreshold,upperPricethreshold]
                    print("default order",slots)
                    print(botOperation.position_side.lower(),"== long ->", botOperation.position_side.lower() == "long")
                    
                    if botOperation.position_side.lower() == "long":
                        slots.reverse()
                    print("new order",slots)
                        
                    for slotPrice in slots:
                        slotPrice = float(self.exchange.price_to_precision(botOperation.symbol, slotPrice))

                        print("checking slot price",slotPrice)
                        if( await self.isSlotInactive(botOperation.id, slotPrice) ):
                            print(f"slot {slotPrice} for {botOperation.symbol} is open")
                            await self.orderManager.create_profit_operation(botOperation.id,slotPrice)

                    
                    
                self.active = not self.active
                    
            