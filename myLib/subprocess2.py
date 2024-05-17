import subprocess

def ejecutar_proceso():
    # Comando que deseas ejecutar (por ejemplo, "dir" en sistemas Windows)
    comando = "dir"

    # Ejecuta el comando y captura la salida
    try:
        salida = subprocess.check_output(comando, shell=True, stderr=subprocess.STDOUT, text=True)
        print("Salida del proceso:")
        print(salida)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")

if __name__ == "__main__":
    ejecutar_proceso()
