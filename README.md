# EasyCab Deployment Notes

The system runs across three different PCs on the same LAN. Two TLS
certificates are provided:

- `cert.pem` – used by the Central and each taxi engine to secure their
  socket communication.
- `registry.crt`/`registry.key` – used by the Registry to serve its HTTPS API.

Make sure the required certificate files are available on every machine so the
clients can validate the remote endpoints.

## PC&nbsp;1 – API Central and Front (with Kafka)
1. Copy `cert.pem` to this machine.
2. Start Kafka/Zookeeper using the provided `docker-compose.yml`.
3. Launch the Central:
   ```bash
   python EC_Central.py <IP_CENTRAL> <PORT_CENTRAL> <IP_KAFKA> <PORT_KAFKA>
   ```
   The Central listens with TLS using `cert.pem`.
4. Run `api_central.py` so the front end can display the map.

## PC&nbsp;2 – CTC and Customers
No special certificates are required. Configure the IPs of PC1 in
`config.json` so requests reach the Central and Kafka.

## PC&nbsp;3 – Registry and Taxis
1. Copy `registry.crt` and `registry.key` to this machine.
2. Start the Registry:
   ```bash
   python EC_Registry.py
   ```
   It serves HTTPS using those certificates.
3. Launch each taxi engine:
   ```bash
   python EC_DE.py
   ```
   The engine verifies the Registry using `registry.crt` and connects to the
   Central using `cert.pem`.
4. Start the corresponding sensor:
   ```bash
   python EC_S.py <IP_SENSOR> <PORT_SENSOR>
   ```

With the certificates in place the engines and the Registry establish secure
channels, preventing eavesdropping of taxi data.

### Launch order
1. `api_central.py` (PC 1, Docker with Kafka)
2. `EC_CTC.py` (PC 2)
3. `EC_Central.py` (PC 1)
4. `EC_Registry.py` (PC 3)
5. `EC_DE.py` instances (PC 3)
6. `EC_S.py` instances (PC 3)
7. `EC_Customer.py` instances (PC 2)