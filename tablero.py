#############################################################
#                        LIBRERIAS                          #
#############################################################
import tkinter as tk
from taxi import *
from destino import *
from variablesGlobales import FILAS, COLUMNAS, TAMANO_CASILLA

#############################################################
#                   VARIABLES GLOBALES                      #
#############################################################
MATRIZ = [[' ' for _ in range(COLUMNAS)] for _ in range(FILAS)]
destinos = []

#############################################################
#                     CLASE TABLERO                         #
#############################################################
class Tablero:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("EasyCab")
        self.numFilas = FILAS
        self.numColumnas = COLUMNAS
        self.tamanyoCelda = TAMANO_CASILLA
        self.frame_tablero = tk.Frame(ventana)
        self.frame_tablero.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self.frame_tablero, width=(self.numFilas + 1) * self.tamanyoCelda, height=(self.numColumnas + 1) * self.tamanyoCelda)
        self.canvas.pack()
        self.dibujarTablero()

        # Crear un frame para las tablas y el título
        self.frame_derecho = tk.Frame(ventana)
        self.frame_derecho.pack(side=tk.RIGHT, fill=tk.Y)


        

    def actualizar_tabla_taxis(self, taxis):
        self.tabla_taxis.delete(1, tk.END)  # Eliminar todas las filas excepto la cabecera
        for taxi in taxis:
            self.tabla_taxis.insert(tk.END, f"{taxi.id}        {taxi.destino.upper()}        {taxi.estado}")

    def actualizar_tabla_clientes(self, clientes):
        self.tabla_clientes.delete(1, tk.END)  # Eliminar todas las filas excepto la cabecera
        for cliente in clientes:
            self.tabla_clientes.insert(tk.END, f"{cliente.id}             {cliente.destino}               {cliente.estado}")


    def dibujarTablero(self):
        for i in range(self.numFilas):
            for j in range(self.numColumnas):
                x0, y0 = (i + 1) * self.tamanyoCelda, (j + 1) * self.tamanyoCelda
                x1, y1 = x0 + self.tamanyoCelda, y0 + self.tamanyoCelda
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="gray")

        for i in range(self.numFilas):
            x = (i + 1) * self.tamanyoCelda + self.tamanyoCelda // 2
            y = self.tamanyoCelda // 2
            self.canvas.create_text(x, y, text=f"{i+1}", font=("Arial", 12))

        for j in range(self.numColumnas):
            x = self.tamanyoCelda // 2
            y = (j + 1) * self.tamanyoCelda + self.tamanyoCelda // 2
            self.canvas.create_text(x, y, text=f"{j+1}", font=("Arial", 12))


    def crearDestino(self, x, y, texto=""):
        global destinos

        destinos.append((x, y, texto))

        color = "lightblue"
        x1 = x * self.tamanyoCelda
        y1 = y * self.tamanyoCelda
        x2 = x1 + self.tamanyoCelda
        y2 = y1 + self.tamanyoCelda
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

        x_text = (x1 + x2) / 2
        y_text = (y1 + y2) / 2
        self.canvas.create_text(x_text, y_text, text=texto, font=("Arial", 12))
    
    def crearCliente(self, x, y, texto=""):
        color = "yellow"
        x1 = x * self.tamanyoCelda
        y1 = y * self.tamanyoCelda
        x2 = x1 + self.tamanyoCelda
        y2 = y1 + self.tamanyoCelda
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
        MATRIZ[y][x] = 'x'  

        x_text = (x1 + x2) / 2
        y_text = (y1 + y2) / 2
        self.canvas.create_text(x_text, y_text, text=texto, font=("Arial", 12))

    def iniciarTaxi(self, x, y, texto=""):
        color = "green"
        x1 = x * self.tamanyoCelda
        y1 = y * self.tamanyoCelda
        x2 = x1 + self.tamanyoCelda
        y2 = y1 + self.tamanyoCelda
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
        MATRIZ[y][x] = 'x' 

        x_text = (x1 + x2) / 2
        y_text = (y1 + y2) / 2
        self.canvas.create_text(x_text, y_text, text=texto, font=("Arial", 12))


    def cambiarColor(self, fila, columna, color, texto=""):
        x0, y0 = (fila+1) * self.tamanyoCelda, (columna+1) * self.tamanyoCelda
        x1, y1 = x0 + self.tamanyoCelda, y0 + self.tamanyoCelda
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="gray")

        x_text = (x0 + x1) / 2
        y_text = (y0 + y1) / 2
        self.canvas.create_text(x_text, y_text, text=texto, font=("Arial", 12))

    def restablerTablero(self):
        for i in range(self.numFilas):
            for j in range(self.numColumnas):
                self.cambiar_color_celda(i, j, "white")

    def recibirDestinos(self, parametro):
        global destinos
        destinos = parametro

        
#############################################################
#     FUNCIÓN QUE ACTUALIZA EL TABLERO CON LA MATRIZ        #
#############################################################
    def actualizarTablero(self, matriz):
        for fila in range(self.numFilas):
            for columna in range(self.numColumnas):
                elemento = matriz[fila][columna]

                for dest in destinos:
                    if dest[0] == fila and dest[1] == columna:
                        self.crearDestino(dest[0], dest[1], dest[2])

                if not elemento:
                    self.cambiarColor(fila, columna, "white", "")
                else:
                    self.cambiarColor(fila, columna, elemento[0].getColor(), elemento[0].id)

#############################################################
#        FUNCIÓN QUE MUESTRA TAXISAUTENTICADOS              #
#############################################################
    def mostrarTaxisAutenticados(self, taxis):
        for taxi in taxis:
            if taxi.estado == "ok":
                color = "green"
            else:
                color = "red"
            self.cambiarColor(taxi.posicionX, taxi.posicionY, color, taxi.id)

#############################################################
#             FUNCIÓN QUE MUESTRA CLIENTES                  #
#############################################################
    def mostrarClientes(self, cliente):
        color = "yellow"
        self.cambiarColor(cliente.posX, cliente.posY, color, cliente.destino.lower())


if __name__ == "__main__":
    ventana = tk.Tk()
    app = Tablero(ventana)
    ventana.mainloop()