#############################################################
#     VARIABLES GLOBALES QUE USAREMOS PARA PARAMETRIZAR     #
#############################################################

import json
import os
import sqlite3

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def _load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as cfg:
            return json.load(cfg)
    return {}

def _save_config(cfg):
    with open(CONFIG_PATH, 'w') as cfg_file:
        json.dump(cfg, cfg_file, indent=4)

CONFIG = _load_config()

# Ruta al directorio compartido en la red utilizada por todos los componentes
# para acceder a la misma base de datos. Debe existir en cada máquina con los
# permisos adecuados.
SHARED_DIRECTORY = r'\\Desktop-ee5cv8c\sd prueba'

# Ubicación del archivo SQLite común
DB_PATH = os.path.join(SHARED_DIRECTORY, 'easycab.db')
#DB_PATH = os.path.join(os.path.dirname(__file__), 'easycab.db')

def get_key(taxi_id):
    """Return the symmetric key for the given taxi ID from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT sym_key FROM taxis2 WHERE id = ? AND active = 1", (taxi_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        if 'conn' in locals():
            conn.close()

def set_key(taxi_id, key):
    """Store the symmetric key for the given taxi ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE taxis2 SET sym_key = ?, active = 1 WHERE id = ?",
        (key, taxi_id),
    )
    conn.commit()
    conn.close()

FILE = CONFIG.get('FILE', 'easycab.db')
FORMATO = CONFIG.get('FORMATO', 'utf-8')
HEADER = CONFIG.get('HEADER', 64)
VER = CONFIG.get('VER', True)
CANTIDADTAXI = CONFIG.get('CANTIDADTAXI', 4)
FILAS = CONFIG.get('FILAS', 20)
COLUMNAS = CONFIG.get('COLUMNAS', 20)
TAMANO_CASILLA = CONFIG.get('TAMANO_CASILLA', 35)
CITY = CONFIG.get('CITY', 'Alicante,ES')
APICTC = CONFIG.get('APICTC', '')
IP_API = CONFIG.get('IP_API', '127.0.0.1')
IP_CTC = CONFIG.get('IP_CTC', '127.0.0.1')
IP_REG = CONFIG.get('IP_REG', '127.0.0.1')
REGISTRY_TOKEN = CONFIG.get('REGISTRY_TOKEN', 'secret-token')
REGISTRY_CERT = CONFIG.get('REGISTRY_CERT', 'registry.crt')
REGISTRY_KEY = CONFIG.get('REGISTRY_KEY', 'registry.key')

def save_config():
    CONFIG['FILE'] = FILE
    CONFIG['FORMATO'] = FORMATO
    CONFIG['HEADER'] = HEADER
    CONFIG['VER'] = VER
    CONFIG['CANTIDADTAXI'] = CANTIDADTAXI
    CONFIG['FILAS'] = FILAS
    CONFIG['COLUMNAS'] = COLUMNAS
    CONFIG['TAMANO_CASILLA'] = TAMANO_CASILLA
    CONFIG['CITY'] = CITY
    CONFIG['APICTC'] = APICTC
    CONFIG['IP_API'] = IP_API
    CONFIG['IP_CTC'] = IP_CTC
    CONFIG['IP_REG'] = IP_REG
    CONFIG['REGISTRY_TOKEN'] = REGISTRY_TOKEN
    CONFIG['REGISTRY_CERT'] = REGISTRY_CERT
    CONFIG['REGISTRY_KEY'] = REGISTRY_KEY
    _save_config(CONFIG)
 #Borovoy,RU

# 172.21.48.1
# Puerto Kafka 9092
#ejecutar central python .\EC_Central.py 192.168.0.101 9000 192.168.0.101 9092

#ejecutar engine python EC_DE.py 192.168.0.101 9092 192.168.0.101 9000 192.168.0.101 9001 2
#ejecutar customer  python EC_Customer.py 192.168.0.101 9092 a 4 4
#python .\EC_S.py 192.168.0.101 9001 

#ejecutar engine python EC_ENGINE.py 192.168.0.101 9092 192.168.0.101 9000 192.168.0.101 9002 3
#ejecutar customer  python EC_Customer.py 192.168.0.101 9092 b 5 5
#python .\EC_S.py 192.168.0.101 9002   





#PARA COMPROBAR QUE FUNCIONA EL CERTIFICADO
#openssl s_client -connect 192.168.0.101:9000 -CAfile cert.pem 

#PARA GENERAR UNO NUEVO EN CLASE

#cambiar en el cnf la IP!!!!

#[ alt_names ]
#IP.1   = 192.168.0.101
#IP.2   = 192.168.0.102
#IP.3   = 192.168.0.103
#DNS.1  = myserver.local

#openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout cert.pem -out cert.pem -config openssl.cnf
#openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout registry.key -out registry.crt -config openssl.cnf
#APIKEY CTC Openweather= 34aaac151d5035a79464cbcd83aef7e6
