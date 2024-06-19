from datetime import datetime
from decimal import Decimal
from typing import Any

from .interfaces.exchange_basic import Num

def obtener_hora_formato_hh_mm_ms():
    # Obtener la hora actual
    ahora = datetime.now()

    # Formatear la hora a HH:MM:ms
    hora_formateada = ahora.strftime("%H:%M:%S::") + f"{ahora.microsecond // 1000:03d}"

    print(hora_formateada)
    
class Utilidades:
    @staticmethod
    def to_float(value: Any) -> float:
        """Convierte un valor de tipo Num a float de manera robusta."""
        if isinstance(value, str):
            return float(value)
        elif isinstance(value, Decimal):
            return float(value)
        return float(value)