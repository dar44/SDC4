#############################################################
#     VARIABLES GLOBALES QUE USAREMOS PARA PARAMETRIZAR     #
#############################################################

import json
import os

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

FILE = CONFIG.get('FILE', 'taxis.db')
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
    _save_config(CONFIG)
 #Borovoy,RU

# 172.21.48.1
# Puerto Kafka 9092
#ejecutar central python .\EC_Central.py 192.168.0.101 9000 192.168.0.101 9092

#ejecutar engine python EC_ENGINE.py 192.168.0.101 9092 192.168.0.101 9000 192.168.0.101 9001 2
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

#openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certSock.pem -out certSock.pem -config openssl.cnf
