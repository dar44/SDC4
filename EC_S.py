#############################################################
#                        LIBRERIAS                          #
#############################################################
import socket
import threading
import time
import sys
import logging
from variablesGlobales import FORMATO

logging.basicConfig(filename='auditoriaEC.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def obtener_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)
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
            logging.error(f"Error de conexión con Engine: {e}")
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
            logging.info("Sensor cambia estado a KO")
        else:
            estado_colision = "ok"
            

#############################################################
#                         MAIN                              #
#############################################################
if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            logging.info("ERROR: argumentos insuficientes en sensor")
            print("Necesito estos argumentos: <ServerIP_E> <Puerto_E>")
            sys.exit(1)

        SERVER = sys.argv[1]
        PORT = int(sys.argv[2])
        ADDR = (SERVER, PORT)

        sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sensor_socket.connect(ADDR)
        ip_address = obtener_ip()
        logging.info(f"Sensor iniciado. IP: {ip_address} Conectado a {ADDR}")
        print(f"Establecida conexión en [{ADDR}]")

        hilo_envio = threading.Thread(target=enviar_mensajes, args=(sensor_socket,))
        hilo_envio.start()

        hilo_entrada = threading.Thread(target=manejar_entrada)
        hilo_entrada.start()

        hilo_envio.join()
        hilo_entrada.join()
        logging.info("Sensor finalizado")
    except KeyboardInterrupt:
        print("Sensor detenido por el usuario.")
        logging.info("Sensor detenido por el usuario.")