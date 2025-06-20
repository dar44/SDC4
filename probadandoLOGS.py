import psutil
import logging
import socket

# Configurar el logging para guardar en un archivo
logging.basicConfig(filename='engine_audit.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def obtener_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def probar_logs():
    ip_address = obtener_ip()
    logging.info(f"Este es un mensaje de prueba. IP: {ip_address}")
    print(f"Mensaje de prueba registrado con IP: {ip_address}")

if __name__ == "__main__":
    probar_logs()