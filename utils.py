from datetime import datetime

def obtener_hora_formato_hh_mm_ms():
    # Obtener la hora actual
    ahora = datetime.now()

    # Formatear la hora a HH:MM:ms
    hora_formateada = ahora.strftime("%H:%M:%S::") + f"{ahora.microsecond // 1000:03d}"

    print(hora_formateada)
