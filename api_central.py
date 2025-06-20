from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import threading
import time

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Variables globales simuladas
taxis = []
matriz = [[[] for _ in range(20)] for _ in range(20)] 
traffic_status = {"status": "OK"}

# Función para obtener destinos desde la base de datos
def obtener_destinos():
    conn = sqlite3.connect('easycab.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, fila, columna FROM destinos')
    destinos = cursor.fetchall()
    conn.close()
    return [{"id": destino[0], "x": destino[1] - 1, "y": destino[2] - 1} for destino in destinos]  # Ajustar índices

# Función para obtener clientes desde la base de datos
def obtener_clientes():
    conn = sqlite3.connect('easycab.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, posX, posY FROM clientes')
    clientes = cursor.fetchall()
    conn.close()
    return [{"id": cliente[0], "x": cliente[1] - 1, "y": cliente[2] - 1} for cliente in clientes]  # Ajustar índices

# Función para obtener taxis desde la base de datos
def obtener_taxis():
    conn = sqlite3.connect('easycab.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, posX, posY, estado, clienteId FROM taxis2')
    taxis = cursor.fetchall()
    conn.close()
    resultado = []
    for taxi in taxis:
        ocupado = taxi[4] not in (None, '-', '')
        resultado.append({
            "id": taxi[0],
            "x": taxi[1] - 1,
            "y": taxi[2] - 1,
            "posX": taxi[1],
            "posY": taxi[2],
            "estado": taxi[3],
            "ocupado": ocupado
        })
    return resultado

@app.route('/map')
def map_page():
    return render_template('index.html')

# Endpoint: Estado del mapa
@app.route('/map_data', methods=['GET'])
def get_map():
    destinos = obtener_destinos()
    clientes = obtener_clientes()
    taxis = obtener_taxis()
    return jsonify({
        "map": matriz,
        "traffic_status": traffic_status["status"],
        "destinos": destinos,
        "clientes": clientes,
        "taxis": taxis
    })

# Endpoint: Actualizar la matriz de taxis
@app.route('/update_map', methods=['POST'])
def update_map():
    global matriz
    data = request.json
    matriz = data["map"]
    return jsonify({"message": "Map updated successfully"}), 200

# Endpoint: Listar taxis autenticados
@app.route('/taxis', methods=['GET'])
def get_taxis():
    taxis_db = obtener_taxis()
    return jsonify([
        {
            "id": taxi["id"],
            "posX": taxi["posX"],
            "posY": taxi["posY"],
            "estado": taxi["estado"],
            "ocupado": taxi["ocupado"]
        }
    for taxi in taxis_db])

# Endpoint: Añadir un taxi
@app.route('/taxis', methods=['POST'])
def add_taxi():
    data = request.json
    taxi = {
        "id": data["id"],
        "posX": data["posX"],
        "posY": data["posY"],
        "estado": data["estado"]
    }
    taxis.append(taxi)
    return jsonify({"message": "Taxi added successfully"}), 201

# Endpoint: Listar clientes
@app.route('/clientes', methods=['GET'])
def get_clientes():
    conn = sqlite3.connect('easycab.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, posX, posY, estado FROM clientes')
    clientes = cursor.fetchall()
    conn.close()
    return jsonify([
        {
            "id": cliente[0],
            "posX": cliente[1],
            "posY": cliente[2],
            "estado": cliente[3]
        }
    for cliente in clientes])
    
# Endpoint: Eliminar un taxi
@app.route('/taxis/<int:taxi_id>', methods=['DELETE'])
def delete_taxi(taxi_id):
    global taxis
    taxis = [taxi for taxi in taxis if taxi["id"] != taxi_id]
    return jsonify({"message": f"Taxi {taxi_id} removed successfully"}), 200

# Endpoint: Estado del tráfico
@app.route('/traffic_status', methods=['GET'])
def get_traffic_status():
    return jsonify({"traffic_status": traffic_status["status"]})

# Endpoint para recibir actualizaciones de tráfico desde EC_CTC
@app.route('/update-traffic', methods=['POST'])
def update_traffic_status():
    data = request.json
    traffic_status["status"] = data.get("status", "KO")
    return jsonify({"message": "Traffic status updated"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)