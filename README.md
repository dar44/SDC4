# EasyCab Deployment Notes

This project is distributed across three PCs within the same LAN. A TLS
certificate is provided in `cert.pem` and must be available to the Central
and to the Engines to secure their socket connection.

## PC 1 – Central and API
1. Copy `cert.pem` to this machine.
2. Start Kafka/Zookeeper using the provided `docker-compose.yml`.
3. Launch the Central with
   ```bash
   python EC_Central.py <IP_CENTRAL> <PORT_CENTRAL> <IP_KAFKA> <PORT_KAFKA>
   ```
   The Central listens using TLS with `cert.pem`.
4. Run `api_central.py` normally so the front‑end can access the updated map.

## PC 2 – CTC and Customers
No special requirement regarding certificates. Ensure that the IPs of PC 1
are configured in `config.json` so requests reach the Central and Kafka.

## PC 3 – Registry and Taxis
1. Copy the same `cert.pem` file from PC 1.
2. Start the Registry with
   ```bash
   python EC_Registry.py
   ```
   It already serves HTTPS using `cert.pem`.
3. Launch each taxi engine:
   ```bash
   python EC_ENGINE.py <IP_KAFKA> <PORT_KAFKA> <IP_CENTRAL> <PORT_CENTRAL> \
       <IP_SENSOR> <PORT_SENSOR> <TAXI_ID>
   ```
   The engine connects to the Central using TLS and requires `cert.pem` to be
   present in the same directory.
4. Start the corresponding sensor with
   ```bash
   python EC_S.py <IP_SENSOR> <PORT_SENSOR>
   ```

With the certificate placed on both PCs, the engines establish a secure
channel with the Central, preventing eavesdropping of taxi data.