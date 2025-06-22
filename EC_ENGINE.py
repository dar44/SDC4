#############################################################
#                        LIBRERIAS                          #
#############################################################
import socket
import sys
import os
import logging
from cliente import Cliente
from variablesGlobales import FORMATO, HEADER, VER, FILAS, COLUMNAS, IP_REG, REGISTRY_TOKEN, get_key
from taxi import Taxi
import threading
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
import time
from tablero import Tablero
import json
from destino import Destino
import tkinter as tk
import requests
import ssl
from utils import encrypt_message, decrypt_message

logging.basicConfig(filename='auditoriaEC.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def obtener_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

#############################################################
#                   VARIABLES GLOBALES                      #
#############################################################
recogido = False
taxis = []
FINALIZADO = False
BASE = False
CambioEstado = False
estado_actual = "ok"
IP = IP_REG

# Función para registrar el taxi
def register_taxi(taxi_id):
    url = f"https://{IP}:5002/register"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {REGISTRY_TOKEN}'
    }
    data = json.dumps({"id": taxi_id})
    try:
        response = requests.post(url, headers=headers, data=data, verify=False)
        if response.status_code == 201:
            logging.info(f"Taxi {taxi_id} registrado correctamente")
        else:
            logging.error(f"Error registrando taxi {taxi_id}: {response.status_code}")
        return response
    except Exception as e:
        logging.error(f"Fallo al registrar taxi {taxi_id}: {e}")
        raise

# Función para dar de baja el taxi
def deregister_taxi(taxi_id):
    url = f"https://{IP}:5002/deregister/{taxi_id}"
    headers = {'Authorization': f'Bearer {REGISTRY_TOKEN}'}
    try:
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 200:
            logging.info(f"Taxi {taxi_id} dado de baja correctamente")
        else:
            logging.error(f"Error al dar de baja taxi {taxi_id}: {response.status_code}")
        return response
    except Exception as e:
        logging.error(f"Fallo al dar de baja taxi {taxi_id}: {e}")
        raise

def menu(taxiID):
    while True:
        print("1. ¿Quieres registrar este taxi?")
        print("2. ¿Quieres eliminar este taxi?")
        print("3. Conectar con central")
        print("4. Salir")
        choice = input("Elige una opción: ")

        if choice == '1':
            response = register_taxi(taxiID)
            if response.status_code == 201:
                print("Taxi registrado exitosamente")
                logging.info(f"Taxi {taxiID} registrado exitosamente")
            else:
                print("Error al registrar el taxi")
                logging.error(f"Error al registrar taxi {taxiID}: {response.status_code}")
        elif choice == '2':
            response = deregister_taxi(taxiID)
            if response.status_code == 200:
                print("Taxi eliminado exitosamente")
                logging.info(f"Taxi {taxiID} eliminado exitosamente")
            else:
                print("Error al eliminar el taxi")
                logging.error(f"Error al eliminar taxi {taxiID}: {response.status_code}")
        elif choice == '3':
            logging.info(f"Taxi {taxiID} conectando con central")
            conectarCentral(taxiID)
            break
        elif choice == '4':
            print("Saliendo...")
            logging.info(f"Taxi {taxiID} sale de la aplicación")
            break
        else:
            print("Opción no válida, por favor intenta de nuevo.")
#############################################################
#        FUNCIONES PARA EL FUNCIONAMIENTO DEL MAPA          #
#############################################################
def imprimirMapa(tablero, ventana):
    global matriz
    
    
    tablero.actualizarTablero(matriz)
    ventana.after(200, imprimirMapa, tablero, ventana)

def iniciarMapa():
    global destinos
    ventana = tk.Tk()
    tablero = Tablero(ventana)
    destinos = leer_mapa('EC_locations.json')
           
    anyadirDestino(destinos)
    ventana.after(200, imprimirMapa, tablero, ventana)
    ventana.mainloop()

def anyadirDestino(destinos):
    global matriz

    for destino in destinos:
        fila = destino.posX
        columna = destino.posY
        if not matriz[fila-1][columna-1]:
            matriz[fila-1][columna-1] = []
        matriz[fila-1][columna-1].append(destino)

def anyadirTaxi(taxi):
    global matriz

    eliminarTaxi(taxi.id)
    limpiarCliente(taxi)
    
    fila = taxi.posicionX
    columna = taxi.posicionY
    if not matriz[fila-1][columna-1]:
        matriz[fila-1][columna-1] = []
    matriz[fila-1][columna-1].insert(0, taxi)

def limpiarCliente(taxi):
    global matriz
    fila = taxi.posicionX
    columna = taxi.posicionY

    if fila == taxi.clienteX and columna == taxi.clienteY:
        if matriz[fila-1][columna-1]:
            matriz[fila-1][columna-1] = [elemento for elemento in matriz[fila-1][columna-1] if not (isinstance(elemento, Cliente) and elemento.id == taxi.clienteId)]

def eliminarTaxi(id):
    global matriz

    for fila in range(len(matriz)):
        for columna in range(len(matriz[0])):
            for idx, taxi in enumerate(matriz[fila][columna]):
                if taxi.id == id:
                    del matriz[fila][columna][idx]
                    return True
                
    return False

def anyadirCliente(taxi):
    global matriz

    clienteX = int(taxi.clienteX)
    clienteY = int(taxi.clienteY)

    if clienteX is None or clienteY is None:
        raise ValueError("Coordenadas del cliente no válidas")

    cliente = Cliente(id=taxi.clienteId, destino=taxi.destino, posX=clienteX, posY=clienteY, estado=taxi.estado)

    fila = cliente.posX
    columna = cliente.posY
    if not matriz[fila-1][columna-1]:
        matriz[fila-1][columna-1] = []
    matriz[fila-1][columna-1].append(cliente)  

#############################################################
#          FUNCIÓN PARA LEER LOCALIZACIONES                 #
#############################################################
def leer_mapa(filename):
    destinos = []
    with open(filename, 'r') as file:
        data = json.load(file)
        for location in data["locations"]:
            id = location["Id"]
            fila, columna = map(int, location["POS"].split(','))
            destino = Destino(id, fila, columna)
            destinos.append(destino)
    return destinos

#############################################################
#                FUNCIÓN PARA ENVIAR                        #
#############################################################
def enviar(msg):
    message = msg.encode(FORMATO)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMATO)
    send_length += b' ' * (HEADER - len(send_length))
    send_data = send_length + message
    conexion.send(send_data)


#############################################################
#       FUNCIÓN QUE MANEJA LOS MENSAJES DE SENSOR           #
#############################################################
def manejarSensor(conn, addr):
    global CambioEstado, estado_actual
    logging.info(f"Sensor conectado desde {addr}")
    print(f"Conectado a {addr}")
    estado_anterior = None  
    try:
        while True:
            pet = conn.recv(4096)
            if not pet:
                break
            mensaje = pet.decode(FORMATO)
            if estado_anterior is None:
                print(f"Sensor ha enviado: {mensaje}")
                estado_anterior = mensaje
                estado_actual = mensaje
            if mensaje == "ko" and estado_anterior != "ko":
                print("Sensor ha enviado: ko")
                CambioEstado = True
                estado_anterior = "ko"
                estado_actual = "ko"
            elif mensaje == "ok" and estado_anterior != "ok":
                print("Sensor ha enviado: ok")
                CambioEstado = True
                estado_anterior = "ok"
                estado_actual = "ok"
            elif mensaje not in ["ko", "ok"]:
                print("Mensaje desconocido.")
    except ConnectionResetError as e:
        logging.error(f"Sensor desconectado: {e}")
        print(f"Sensor cerrado, esperando de nuevo su conexión...")
        if estado_actual == "ok":
            estado_anterior = "ko"
            estado_actual = "ko"
            CambioEstado = True
    finally:
        conn.close()
        

#############################################################
#       FUNCIÓN QUE INICIA LA CONEXIÓN CON SENSOR           #
#############################################################
def iniciar_servidor():
    global estado_actual, CambioEstado
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR_S)
    server.listen()
    logging.info(f"Esperando conexión de sensor en {ADDR_S}")
    print(f"Escuchando conexión con Sensor en [{ADDR_S}]")

    while True:
        conn, addr = server.accept()
        if estado_actual == "ko":
            estado_actual = "ok"
            CambioEstado = True 
        manejarSensor(conn, addr)

#############################################################
#             FUNCIÓN QUE CONECTA CON CENTRAL               #
#############################################################
def conectarCentral(taxiID):
    #global conexion

    #ADDR_C = (SERVER_C, PORT_C)
    #context = ssl._create_unverified_context()
    #with socket.create_connection(ADDR_C) as sock:
    #    conexion = context.wrap_socket(sock, server_hostname=SERVER_C)
    #    print(f"Establecida conexión con Central en [{ADDR_C}]")
    #    enviar(taxiID)
    global conexion
    conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conexion.connect(ADDR_C)
        logging.info(f"Taxi {taxiID} conectado con Central en {ADDR_C}")
        print(f"Establecida conexión con Central en [{ADDR_C}]")
        enviar(taxiID)
    except Exception as e:
        logging.error(f"No se pudo conectar con Central: {e}")
        print("Imposible conectar con Central")


#############################################################
#    FUNCIÓN QUE ESPERA COMUNICACIÓN DE CENTRAL POR KAFKA   #
#############################################################
def esperandoTaxi( ):
    global CambioEstado
    global taxis
    #print("Esperando taxi")
    consumer_conf = {
        'bootstrap.servers': f'{SERVER_K}:{PORT_K}',
        'group.id': 'grupo_consumidor3',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_conf)
    topicMovimiento = 'movimiento'

    consumer.subscribe([topicMovimiento])
    print("Recibiendo mensaje")

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f'Error while receiving message: {msg.error()}' )
                break

        mensaje_completo = msg.value().decode(FORMATO)
        # Nuevo formato: id%mensajeCifrado%token
        try:
            taxi_id, mensaje_cifrado, tokenTaxi = mensaje_completo.split('%')
            key = get_key(taxi_id)
            if not key:
                print(f"No se encontró clave para el taxi {taxi_id}")
                continue
            mensaje = decrypt_message(mensaje_cifrado.strip(), key)
        except Exception as e:
            print(f"Error al descifrar mensaje para taxi {taxi_id}: {e}")
            continue
        #print("Mensaje recibido")
        consumer.close()
        taxiData = mensaje.split(':')
        taxi = Taxi(
            id=taxiData[0],
            estado=taxiData[1],
            posicionX=int(taxiData[2]),
            posicionY=int(taxiData[3]),
            destino=taxiData[4],
            destinoX=int(taxiData[5]),
            destinoY=int(taxiData[6]),
            ocupado=taxiData[7],
            clienteX=int(taxiData[8]),
            clienteY=int(taxiData[9]),
            clienteId = taxiData[10],
            base = int(taxiData[11])
        )
        #print("Tu puto taxi")
        anyadirTaxi(taxi)
        anyadirCliente(taxi)
        if CambioEstado:
            if taxi.estado == "ko":
                taxi.estado = "ok"
                CambioEstado = False
            else:
                taxi.estado = "ko"
                CambioEstado = False
        #print(taxi)
        taxis.append(taxi)
        if taxi.base == 1:
            taxi = moverTaxiBase(taxi)
        else :
            taxi = moverTaxiCliente(taxi)
        #print("tu puto taxi se ha movido")
        enviarMovimiento(taxi)
        break

#############################################################
#      FUNCIÓN QUE ENVÍA COMUNICACIÓN A CENTRAL POR KAFKA   #
#############################################################
def enviarMovimiento(taxi):
    global taxis
    producer_conf = {'bootstrap.servers': f'{SERVER_K}:{PORT_K}'}
    producer = Producer(producer_conf)
    

    topicRecorrido = 'recorrido'
    key = get_key(taxi.id)
    if not key:
        print(f"No se encontró clave para el taxi {taxi.id}")
        return
    mensaje_cifrado = encrypt_message(taxi.imprimirTaxi(), key)
    mensaje = f"{taxi.id}%{mensaje_cifrado}"
    producer.produce(topicRecorrido, key=None, value=mensaje.encode(FORMATO), callback=comprobacion)
    time.sleep(1)
    producer.flush()
    
    if taxi.estado == "END":
        esperandoTaxi()
    if taxi.estado == "ENDB":
        print("Taxi desconectado")
        os._exit(0)
    else:
        reciboMapa()

def comprobacion(error, msg):
    if error is not None:
        if VER: print(f'La entrega del mensaje falló: {error}')
    else:
        if VER: print(f'Enviado taxi con nueva la nueva posición')

#############################################################
#          FUNCIÓN PARA QUE HAGA SEGURO LOS ENTEROS         #
#############################################################
def safe_int(value, default=None):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

#############################################################
#    FUNCIÓN QUE ESPERA COMUNICACIÓN DE CENTRAL POR KAFKA   #
#############################################################
def reciboMapa():
    global FINALIZADO
    global BASE
    global recogido
    global taxis 
    global CambioEstado
    print("Taxi listo para moverse")
    consumer_conf = {
        'bootstrap.servers': f'{SERVER_K}:{PORT_K}',
        'group.id': 'grupo_consumidor4',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_conf)
    topicMapa = 'mapa'

    consumer.subscribe([topicMapa])
    #print("Recibiendo mensaje")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f'Error while receiving message: {msg.error()}' )
                break
        mensaje = msg.value().decode(FORMATO)
        taxis = []
        consumer.close()
        taxisstr = mensaje.split("/")
        for taxistr in taxisstr:
            taxiData = taxistr.split(':')
            taxi = Taxi(
                id=taxiData[0],
                estado=taxiData[1],
                posicionX=int(taxiData[2]),
                posicionY=int(taxiData[3]),
                destino=taxiData[4],
                destinoX=int(taxiData[5]),
                destinoY=int(taxiData[6]),
                ocupado=taxiData[7],
                clienteX=int(taxiData[8]),
                clienteY=int(taxiData[9]),
                clienteId=taxiData[10],
                base=int(taxiData[11])
            )

            taxis.append(taxi)
        #print("Tu lista taxi de taxis")
        for taxi in taxis:
            #print(taxi)
            if taxi.id == taxiID:
                if CambioEstado:
                    if taxi.estado == "ko":
                        taxi.estado = "ok"
                        CambioEstado = False
                    else:
                        taxi.estado = "ko"
                        CambioEstado = False
                if taxi.posicionX == taxi.clienteX and taxi.posicionY == taxi.clienteY:
                    recogido = True

                if taxi.base == 1:
                    taxi = moverTaxiBase(taxi)
                elif recogido:
                    taxi = moverTaxi(taxi)
                else :
                    taxi = moverTaxiCliente(taxi)
                    
                if FINALIZADO:
                    taxi.ocupado = False
                    taxi.destino = '-'
                    taxi.estado = "END"
                    
                    recogido = False
                    FINALIZADO = False
                    enviarMovimiento(taxi)
                if BASE:
                    taxi.ocupado = False
                    taxi.destino = '-'
                    taxi.estado = "ENDB"
                    
                    recogido = False
                    BASE = False
                    enviarMovimiento(taxi)
                else:
                    enviarMovimiento(taxi)

                break
        break

##########################################################################
#   FUNCIÓN QUE CALCULA LA DIRECCIÓN POR LA QUE IRÁ (GEOMETRÍA ESFÉRICA) #
##########################################################################
def calcular_direccion(inicio, final):
    distancia_directa = final - inicio
    distancia_wrap_around = (final - inicio + 20) % 20
    distancia_wrap_around_neg = (inicio - final + 20) % 20

    if abs(distancia_directa) <= abs(distancia_wrap_around) and abs(distancia_directa) <= abs(distancia_wrap_around_neg):
        return 1 if distancia_directa > 0 else -1 if distancia_directa < 0 else 0
    elif abs(distancia_wrap_around) < abs(distancia_wrap_around_neg):
        return 1
    else:
        return -1   
    
#############################################################
#               FUNCIÓN QUE MUEVE EL TAXI A LA BASE         #
#############################################################
def moverTaxiBase(taxi):
    global BASE 
    inicioX = taxi.posicionX
    inicioY = taxi.posicionY
    finalX = 1
    finalY = 1
    print("Taxi situado en ", inicioX, ", ", inicioY)
    print("La base esta en ", finalX, ", ", finalY)

    direccion_x = calcular_direccion(inicioX, finalX)
    direccion_y = calcular_direccion(inicioY, finalY)

    
    if taxi.estado == "ok":
        inicioX = (inicioX + direccion_x - 1) % 20 + 1
        inicioY = (inicioY + direccion_y - 1) % 20 + 1

    if inicioX == finalX and inicioY == finalY:
        print(f"Nueva posición: {inicioX}, {inicioY}")
        print("¡Ya has llegado al destino", "\n") 
        BASE = True
    else:
        print(f"Nueva posición: {inicioX}, {inicioY}", "\n")

    taxi.posicionX = inicioX
    taxi.posicionY = inicioY

    anyadirTaxi(taxi)

    return taxi

        
#############################################################
#               FUNCIÓN QUE MUEVE EL TAXI                   #
#############################################################
def moverTaxi(taxi):
    global FINALIZADO 
    inicioX = taxi.posicionX
    inicioY = taxi.posicionY
    finalX = taxi.destinoX
    finalY = taxi.destinoY
    print("Taxi situado en ", inicioX, ", ", inicioY)
    print("El destino del cliente se encuentra en ", finalX, ", ", finalY)

    direccion_x = calcular_direccion(inicioX, finalX)
    direccion_y = calcular_direccion(inicioY, finalY)

    
    if taxi.estado == "ok":
        inicioX = (inicioX + direccion_x - 1) % 20 + 1
        inicioY = (inicioY + direccion_y - 1) % 20 + 1

    if inicioX == finalX and inicioY == finalY:
        print(f"Nueva posición: {inicioX}, {inicioY}")
        print("¡Ya has llegado al destino", "\n") 
        FINALIZADO = True
    else:
        print(f"Nueva posición: {inicioX}, {inicioY}", "\n")

    taxi.posicionX = inicioX
    taxi.posicionY = inicioY

    anyadirTaxi(taxi)

    return taxi

#############################################################
#           FUNCIÓN QUE MUEVE EL TAXI AL CLIENTE            #
#############################################################
def moverTaxiCliente(taxi):
    inicioX = taxi.posicionX
    inicioY = taxi.posicionY
    finalX = taxi.clienteX
    finalY = taxi.clienteY
    print("Taxi situado en ", inicioX, ", ", inicioY)
    print("Recojo al cliente en ", finalX, ", ", finalY)

    direccion_x = calcular_direccion(inicioX, finalX)
    direccion_y = calcular_direccion(inicioY, finalY)

    if taxi.estado == "ok":
        inicioX = (inicioX + direccion_x - 1) % 20 + 1
        inicioY = (inicioY + direccion_y - 1) % 20 + 1

    if inicioX == finalX and inicioY == finalY:
        print(f"Nueva posición: {inicioX}, {inicioY}")
        print("¡Ya he regocido al cliente!", "\n") 
    else:
        print(f"Nueva posición: {inicioX}, {inicioY}", "\n")

    taxi.posicionX = inicioX
    taxi.posicionY = inicioY

    anyadirTaxi(taxi)

    return taxi

#############################################################
#          FUNCIÓN QUE INICIALIZA LA MATRIZ VACIA           #
#############################################################
def matrizVACIA():
    global FILAS
    global COLUMNAS

    return [[[] for _ in range(FILAS)] for _ in range(COLUMNAS)]

matriz = matrizVACIA()

#############################################################
#                         MAIN                              #
#############################################################
if __name__ == "__main__":
    try:
        if  (len(sys.argv) == 8):
            ip_address = obtener_ip()
            logging.info(f"Engine iniciado. IP: {ip_address}")

            SERVER_K = sys.argv[1]
            PORT_K = int(sys.argv[2])
            ADDR_K = (SERVER_K, PORT_K)
            SERVER_C = sys.argv[3]
            PORT_C = int(sys.argv[4])
            ADDR_C = (SERVER_C, PORT_C)
            SERVER_S = sys.argv[5]
            PORT_S = int(sys.argv[6])
            ADDR_S = (SERVER_S, PORT_S)
            taxiID = str(sys.argv[7])

            # Registrar el taxi
            menu(taxiID)
            #map_thread = threading.Thread(target=iniciarMapa)
            #map_thread.start()

            destinos = leer_mapa('EC_locations.json')

            kafka_thread = threading.Thread(target=iniciar_servidor)
            kafka_thread.start()

            kafka_thread = threading.Thread(target=esperandoTaxi)
            kafka_thread.start()
        else:
            print("Necesito estos argumentos: <ServerIP_K> <Puerto_K> <ServerIP_C> <Puerto_C> <ServerIP_S> <Puerto_S> <TAXI_ID")
            logging.info("ERROR: Argumentos insuficientes para iniciar el Engine")
    except KeyboardInterrupt:
        print("Engine detenido por el usuario.")
        logging.info("Engine detenido por el usuario.")