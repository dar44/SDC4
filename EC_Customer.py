#############################################################
#                        LIBRERIAS                          #
#############################################################
import sys
from cliente import Cliente
from variablesGlobales import FORMATO, VER
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
import time
import json

#############################################################
#                   VARIABLES GLOBALES                      #
#############################################################
HEADER = 64
FORMAT = FORMATO
FIN ="FIN"
cliente = None
destinos = []

#############################################################
#              FUNCIÓN PARA LEER DESTINOS                   #
#############################################################
def leerDestinos(filename, posicionX, posicionY): 
    global cliente
    global destinos
    with open(filename, 'r') as file:
        data = json.load(file)
        for request in data["Requests"]:
            valor = request["Id"]
            if valor:
                destinos.append(valor)

        posX = posicionX
        posY = posicionY
        estado = "Sin Taxi"
        destino = destinos[0]
        cliente = Cliente(CLIENTEID, destino, posX, posY, estado)

        print("Ha sido registrado el siguiente cliente.")
        print(cliente, "\n")

def comprobacion(error, msg):
    if error is not None:
        if VER: print(f'La entrega del mensaje falló: {error}')
    else:
        pass

#############################################################
#        FUNCIÓN QUE MANDA EL SERVICIO DEL CLIENTE          #
#############################################################
def enchufoAplicacion(mensajeNuevo):
    producer_conf = {'bootstrap.servers': f'{SERVER_K}:{PORT_K}'}
    producer = Producer(producer_conf)

    topicPos = 'posicion'
    if mensajeNuevo == "END":
        mensaje = "END"
        print(mensaje)
        producer.produce(topicPos, key=None, value=mensaje.encode(FORMATO), callback=comprobacion)
        producer.flush()

    else:
        mensaje = cliente.imprimirCliente()
        #print(mensaje)
        producer.produce(topicPos, key=None, value=mensaje.encode(FORMATO), callback=comprobacion)
        producer.flush()
        print("Servicio pedido" , "\n", "Si no se le consigue asignar un taxi se le notificará.", "\n")
        escuchoSiLlego()

#############################################################
#       FUNCIÓN QUE ESCUCHA POR KAFKA A CENTRAL             #
#############################################################
def escuchoSiLlego():
    global cliente
    global CLIENTEID
    consumer_conf = {
        'bootstrap.servers': f'{SERVER_K}:{PORT_K}',
        'group.id': f'grupo_consumidorr_{CLIENTEID}',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False  # Desactivar autocommit
    }
    consumer = Consumer(consumer_conf)
    topicDestino = 'destino'

    consumer.subscribe([topicDestino])
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
        else:
            mensaje = msg.value().decode(FORMATO)
            split = mensaje.split(':')
            # print("Id recibido: " + split[0])
            # print("Id cliente: " + CLIENTEID)

            if split[0] == CLIENTEID:
                consumer.commit(msg, asynchronous=False)  # Realizar commit manual
                #print(mensaje)
                if len(split) < 3:
                    if split[1] == "Taxi desconectado":
                        print("Taxi desconectado")
                    else: 
                        print("No hay taxis disponibles")
                    consumer.close()
                    sys.exit()
                    break
                else:
                    #print("Se te ha asignado el taxi.")
                    cliente.posX = int(split[3])
                    cliente.posY = int(split[4])
                    # print("Tu cliente")
                    # print(cliente)
                    consumer.close()
                    actualizarDestinos()
                    break
    
#############################################################
#             FUNCIÓN QUE ACTUALIZA DESTINOS                #
#############################################################
def actualizarDestinos():
    global destinos
    destinos.pop(0)
    if len(destinos) == 0:
        print("Ya no hay más destinos")
        mensaje = "END"
        enchufoAplicacion(mensaje)
    else:
        destino = destinos[0]
        cliente.destino = destino
        print("Ya ha llegado a su destino")
        #print(cliente)
        print("Espere 4 segundos y pida un taxi nuevo", "\n")
        time.sleep(4)
        mensaje = "Otro taxi"
        enchufoAplicacion(mensaje)


#############################################################
#                         MAIN                              #
#############################################################
if __name__ == "__main__":
    try:
        if len(sys.argv) == 6:
            SERVER_K = sys.argv[1]   #IP del servidor de kafka
            PORT_K = int(sys.argv[2])
            ADDR = (SERVER_K, PORT_K)
            CLIENTEID = str(sys.argv[3])
            posicionX = int(sys.argv[4])
            posicionY = int(sys.argv[5])
            archivo = "EC_Requests_" + CLIENTEID + ".json"
            primerMensaje = "Primer mensaje"
            leerDestinos(archivo, posicionX, posicionY)
            enchufoAplicacion(primerMensaje)
        else:
            print("Necesito estos argumentos: <KAFKA IP> <Puerto KAFKA> <ID CLIENTE>")
    except KeyboardInterrupt:
        print("Cliente detenido por el usuario.")
    #establecer_conexion()