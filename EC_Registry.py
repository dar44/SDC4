from flask import Flask, request, jsonify
import sqlite3
import atexit
import os
import logging
import socket

def load_registry_token():
    secret_file = 'registry_secret.txt'
    try:
        with open(secret_file, 'r') as sf:
            return sf.read().strip()
    except FileNotFoundError:
        return None

REGISTRY_TOKEN = load_registry_token()

def token_required(f):
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        token = auth.split(' ', 1)[1]
        if token != REGISTRY_TOKEN:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper

app = Flask(__name__)

logging.basicConfig(filename='auditoriaEC.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def obtener_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

#db_path = os.path.join(os.path.dirname(__file__), 'easycab.db')
# Ruta al directorio compartido en la red
shared_directory = r'\\Desktop-ee5cv8c\sd prueba'
db_path = os.path.join(shared_directory, 'easycab.db')

# Initialize the database
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS taxis (
            id INTEGER PRIMARY KEY,
            estado TEXT DEFAULT 'ok',
            posicionX INTEGER DEFAULT 1,
            posicionY INTEGER DEFAULT 1,
            destino TEXT DEFAULT '-',
            destinoX INTEGER DEFAULT 0,
            destinoY INTEGER DEFAULT 0,
            ocupado BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Clear the taxis table
def clear_taxis_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM taxis')
    conn.commit()
    conn.close()
    logging.info("Tabla de taxis vaciada")

# Register a new taxi
@app.route('/register', methods=['POST'])
@token_required
def register_taxi():
    data = request.get_json()
    taxi_id = data.get('id')
    
    if not taxi_id:
        logging.error("Registro fallido: Taxi ID requerido")
        return jsonify({"error": "Taxi ID is required"}), 400
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO taxis (id, estado, posicionX, posicionY, destino, destinoX, destinoY, ocupado)
        VALUES (?, 'ok', 1, 1, '-', 0, 0, 0)
    ''', (taxi_id,))
    conn.commit()
    conn.close()
    
    logging.info(f"Taxi {taxi_id} registrado en Registry")
    return jsonify({"message": "Taxi registered successfully"}), 201

# Deregister a taxi
@app.route('/deregister/<int:taxi_id>', methods=['DELETE'])
def deregister_taxi(taxi_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM taxis WHERE id = ?', (taxi_id,))
    cursor.execute('DELETE FROM taxis2 WHERE id = ?', (taxi_id,))
    conn.commit()
    conn.close()
    
    logging.info(f"Taxi {taxi_id} eliminado del Registry")
    return jsonify({"message": "Taxi deregistered successfully"}), 200

# Check if a taxi is registered
@app.route('/is_registered/<int:taxi_id>', methods=['GET'])
def is_registered(taxi_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM taxis WHERE id = ?', (taxi_id,))
    taxi = cursor.fetchone()
    conn.close()
    
    if taxi:
        logging.info(f"Comprobación registro taxi {taxi_id}: registrado")
        return jsonify({"registered": True}), 200
    else:
        logging.info(f"Comprobación registro taxi {taxi_id}: no registrado")
        return jsonify({"registered": False}), 404

if __name__ == '__main__':
    init_db()
    atexit.register(clear_taxis_table)
    app.run(debug=True, host='0.0.0.0', port=5002, ssl_context=('cert.pem', 'cert.pem'))