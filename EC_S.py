#############################################################
#                        LIBRERIAS                          #
#############################################################
import socket
import threading
import time
import sys
from variablesGlobales import FORMATO

#############################################################
#                   VARIABLES GLOBALES                      #
#############################################################
estado_colision = "ok"

#############################################################
#               FUNCION QUE ENVIA EL ESTADO                 #
#############################################################
def enviar_mensajes(sensor):
    global estado_colision
    while True:
        try:
            sensor.send(estado_colision.encode(FORMATO))
            time.sleep(1)  # Enviar mensaje cada segundo
        except ConnectionAbortedError as e:
            print(f"Error de conexión: {e}")
            break

#############################################################
#     FUNCION QUE MANEJA EL MENSAJE QUE SE ENVIA            #
#############################################################
def manejar_entrada():
    global estado_colision
    while True:
        input("Presiona cualquier tecla para cambiar el estado de colisión: ")
        if estado_colision == "ok":
            estado_colision = "ko"
        else:
            estado_colision = "ok"

#############################################################
#                         MAIN                              #
#############################################################
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Necesito estos argumentos: <ServerIP_E> <Puerto_E>")
        sys.exit(1)

    SERVER = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (SERVER, PORT)

    sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sensor_socket.connect(ADDR)
    print(f"Establecida conexión en [{ADDR}]")

    hilo_envio = threading.Thread(target=enviar_mensajes, args=(sensor_socket,))
    hilo_envio.start()

    hilo_entrada = threading.Thread(target=manejar_entrada)
    hilo_entrada.start()

    hilo_envio.join()
    hilo_entrada.join()