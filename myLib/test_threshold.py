class BotOperationHelper:
    @staticmethod
    def find_enclosing_thresholds(entry_price, current_price, threshold):
        nearer_threshold = entry_price
        farther_threshold = entry_price
        # Calcular umbral inferior más cercano
        while nearer_threshold > current_price:
            farther_threshold = nearer_threshold / (1 + (threshold / 100))
            if farther_threshold <= current_price:
                break
            nearer_threshold = farther_threshold
        return farther_threshold, nearer_threshold

# Ejemplo de uso
entry_price = 100
current_price = 50
threshold = 1

helper = BotOperationHelper()
lower_threshold, upper_threshold = helper.find_enclosing_thresholds(entry_price, current_price, threshold)

print(f"Umbral inferior más cercano: {lower_threshold}")
print(f"Umbral superior más cercano: {upper_threshold}")
