import tkinter as tk
from tkinter import scrolledtext

# Función para simular la salida de la consola
def simular_consola():
    consola.insert(tk.END, "Salida de ejemplo\n")
    consola.yview(tk.END)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Ventana con Botones y Consola")

# Crear un botón
boton = tk.Button(ventana, text="Ejecutar Función", command=simular_consola)
boton.pack()

# Crear un recuadro de texto con barra de desplazamiento
consola = scrolledtext.ScrolledText(ventana, width=40, height=10)
consola.pack()

# Iniciar el bucle principal de la ventana
ventana.mainloop()
