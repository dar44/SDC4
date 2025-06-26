from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
import sqlite3
import threading
import os
import time
from variablesGlobales import IP_API, IP_CTC



app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Variables globales simuladas
taxis = []
matriz = [[[] for _ in range(20)] for _ in range(20)] 
traffic_status = {"status": "OK"}
current_city = "Almoradi, ES"
current_temperature = 0.0
LOG_FILE = 'auditoriaEC.log'

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
            "ocupado": ocupado,
            "clienteId": taxi[4]
        })
    return resultado

@app.route('/map')
def map_page():
    return render_template('index.html', ip_api=IP_API, ip_ctc=IP_CTC)

# Página independiente para visualizar la auditoría de seguridad
@app.route('/audit')
def audit_page():
    return render_template('audit.html', ip_api=IP_API)
    
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
            "ocupado": taxi["ocupado"],
            "clienteId": taxi["clienteId"],
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
            "estado": cliente[3],
            
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
    return jsonify({
        "traffic_status": traffic_status["status"],
        "city": current_city,
        "temperature": round(current_temperature, 2)
        
    })

# Endpoint para recibir actualizaciones de tráfico desde EC_CTC
@app.route('/update-traffic', methods=['POST'])
def update_traffic_status():
    data = request.json
    global current_city, current_temperature
    traffic_status["status"] = data.get("status", "KO")
    current_city = data.get("city", current_city)
    if "temperature" in data:
        current_temperature = data["temperature"]
    return jsonify({"message": "Traffic status updated"}), 200

# ---------------------------------------------------------------------------
# Auditoría de seguridad
# ---------------------------------------------------------------------------

def tail_f(log_file):
    """Generator para transmitir nuevas entradas del archivo de log."""
    with open(log_file, 'r') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            yield f"data: {line.strip()}\n\n"


@app.route('/logs', methods=['GET'])
def get_logs():
    """Devuelve las últimas 100 líneas del log de auditoría."""
    if not os.path.exists(LOG_FILE):
        return jsonify({"logs": []})
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()[-100:]
    return jsonify({"logs": [line.strip() for line in lines]})


@app.route('/logs/stream')
def stream_logs():
    """Stream de nuevas entradas del log de auditoría mediante SSE."""
    return Response(tail_f(LOG_FILE), mimetype='text/event-stream')

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("API Central detenida por el usuario.")
        