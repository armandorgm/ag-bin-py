# ventana_principal.py
import tkinter as tk

class VentanaPrincipal:
    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.frame.pack()
        self.boton_abrir = tk.Button(self.frame, text="Abrir Ventana Secundaria")
        self.boton_abrir.pack()
