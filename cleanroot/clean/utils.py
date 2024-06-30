from datetime import datetime
from decimal import Decimal
from typing import Any
import re
import random
import string
import uuid



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


    @staticmethod
    def generar_id_unico():
        # Define los caracteres permitidos
        caracteres_permitidos = string.ascii_letters + string.digits + "_-."

        # Genera una cadena aleatoria de longitud entre 1 y 36
        longitud = random.randint(1, 36)
        id_unico = ''.join(random.choice(caracteres_permitidos) for _ in range(longitud))

        # Verifica si cumple con la regla regex
        if re.match(r"^[\.A-Z\:/a-z0-9_-]{1,36}$", id_unico):
            #         ^[\.A-Z\:/a-z0-9_-]{1,36}$
            return id_unico
        else:
            # Si no cumple, intenta nuevamente
            return Utilidades.generar_id_unico()
        
    @staticmethod
    def generarIdUnico():
        # Genera un UUID único
        
        id_unico = str(uuid.uuid4())
        if re.match(r"^[\.A-Z\:/a-z0-9_-]{1,36}$", str(id_unico)):
            #         ^[\.A-Z\:/a-z0-9_-]{1,36}$
            return id_unico
        else:
            # Si no cumple, intenta nuevamente
            print(id_unico, "no cumple con las reglas")
            return Utilidades.generarIdUnico()
        return 



if __name__ == "__main__":
    # Ejemplo de uso
    mi_id_unico = Utilidades.generar_id_unico()
    print(f"ID único generado: {mi_id_unico}")
    
    id2 = str(Utilidades.generarIdUnico())
    print(f"ID2: {id2} lenght:{len(id2)}")
