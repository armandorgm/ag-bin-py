def is_within_threshold(reference, value, percentage):
    threshold_amount = reference * (percentage / 100)
    return abs(reference - value) <= threshold_amount

# Ejemplo de uso
reference_value = 100
value_to_check = 111
threshold_percentage = 10

is_within = is_within_threshold(reference_value, value_to_check, threshold_percentage)
print(f"El valor {value_to_check} está dentro del {threshold_percentage}% de {reference_value}: {is_within}")
