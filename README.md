# Notas de despliegue de EasyCab

El sistema se ejecuta en tres PCs diferentes dentro de la misma LAN. Se suministran dos certificados TLS:

- `cert.pem` – usado por la Central y cada motor de taxi para cifrar la comunicación por sockets.
- `registry.crt` / `registry.key` – utilizados por el Registro para exponer su API HTTPS.

Asegúrate de que estos certificados estén presentes en cada máquina para que los clientes puedan validar los servicios remotos.
Install the Python dependencies with `pip install -r requirements.txt` on each machine.

## PC 1 – APICentral, Central y Frontend (con Kafka)
1. Copia `cert.pem` en esta máquina.
2. Inicia Kafka y Zookeeper mediante el `docker-compose.yml` provisto.
3. Ejecuta la Central:
   ```bash
   python EC_Central.py <IP_CENTRAL> <PUERTO_CENTRAL> <IP_KAFKA> <PUERTO_KAFKA>
   ```
   La Central escucha con TLS usando `cert.pem`.
4. Ejecuta `api_central.py` para que el front muestre el mapa.

## PC 2 – CTC y Clientes
No se requieren certificados. Configura en `config.json` las IP de la PC 1 para que las peticiones alcancen la Central y Kafka.

## PC 3 – Registro y Taxis
1. Copia `registry.crt` y `registry.key` en esta máquina.
2. Arranca el Registro:
   ```bash
   python EC_Registry.py
   ```
   Sirve HTTPS con esos certificados.
3. Inicia cada motor de taxi:
   ```bash
   python EC_DE.py
   ```
   Verifica el Registro con `registry.crt` y se conecta a la Central usando `cert.pem`.
4. Inicia el sensor correspondiente:
   ```bash
   python EC_S.py <IP_SENSOR> <PUERTO_SENSOR>
   ```

Con los certificados correctamente instalados, los motores y el Registro establecen canales seguros y evitan la interceptación de datos.

### Orden de lanzamiento
1. `api_central.py` (PC 1, Docker con Kafka)
2. `EC_CTC.py` (PC 2)
3. `EC_Central.py` (PC 1)
4. `EC_Registry.py` (PC 3)
5. `EC_DE.py` (PC 3)
6. `EC_S.py` (PC 3)
7. `EC_Customer.py` (PC 2)