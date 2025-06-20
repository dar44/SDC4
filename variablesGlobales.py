#############################################################
#     VARIABLES GLOBALES QUE USAREMOS PARA PARAMETRIZAR     #
#############################################################
FILE = 'taxis.db'
FORMATO = 'utf-8'
HEADER = 64
VER = True
CANTIDADTAXI = 4
FILAS = 20
COLUMNAS = 20
TAMANO_CASILLA = 35
CITY = 'Alicante,ES'
APICTC = 'c31073c6041c4725d2cf4e489f449034'
IP_API = '192.168.1.83'
IP_CTC = '192.168.1.83'
IP_REG = '192.168.1.83'
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
