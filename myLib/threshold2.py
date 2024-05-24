class BotOperationHelper:
    @staticmethod
    def find_enclosing_thresholds(entry_price, current_price, threshold):
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

# Ejemplo de uso
entry_price = 100
current_price = 99.9  # Ejemplo con precio actual superior al precio de entrada
threshold = 1

helper = BotOperationHelper()
lower_threshold, upper_threshold = helper.find_enclosing_thresholds(entry_price, current_price, threshold)

print(f"Umbral inferior más cercano: {lower_threshold}")
print(f"Umbral superior más cercano: {upper_threshold}")
