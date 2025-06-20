from flask import Flask, request, jsonify
import sqlite3
import atexit
import os

app = Flask(__name__)

# Ruta al directorio compartido en la red
shared_directory = r'\\BONILLA\abab4-ggr23'
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

# Register a new taxi
@app.route('/register', methods=['POST'])
def register_taxi():
    data = request.get_json()
    taxi_id = data.get('id')
    
    if not taxi_id:
        return jsonify({"error": "Taxi ID is required"}), 400
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO taxis (id, estado, posicionX, posicionY, destino, destinoX, destinoY, ocupado) 
        VALUES (?, 'ok', 1, 1, '-', 0, 0, 0)
    ''', (taxi_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Taxi registered successfully"}), 201

# Deregister a taxi
@app.route('/deregister/<int:taxi_id>', methods=['DELETE'])
def deregister_taxi(taxi_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM taxis WHERE id = ?', (taxi_id,))
    conn.commit()
    conn.close()
    
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
        return jsonify({"registered": True}), 200
    else:
        return jsonify({"registered": False}), 404

if __name__ == '__main__':
    init_db()
    atexit.register(clear_taxis_table)
    app.run(debug=True, host='0.0.0.0', port=5002)