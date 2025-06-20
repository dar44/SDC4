import requests
import time
import os
from flask import Flask, jsonify, request
from variablesGlobales import CONFIG, IP_API, save_config
import threading

app = Flask(__name__)

# Variables globales para OpenWeather
IP = IP_API
urlUpdate = f"http://{IP}:5000/update-traffic"
traffic_status = {"status": "OK"}

def fetch_temperature_and_update_central():
    while True:
        try:
            # Leer el nombre de la ciudad desde la configuración
            CITYNAME = CONFIG.get('CITY', 'Alicante,ES')
            api_key = CONFIG.get('APICTC', '')

            url = f'https://api.openweathermap.org/data/2.5/weather?q={CITYNAME}&appid={api_key}'
            # Consultar OpenWeather
            response = requests.get(url)
            data = response.json()
            temperature = data['main']['temp'] - 273.15  # Convertir a Celsius
            traffic_status["status"] = "KO" if temperature < 0 else "OK"
            
            # Enviar estado de tráfico al API central
            response = requests.post(urlUpdate, json={"status": traffic_status["status"]})
            print(f"POST to {urlUpdate}: Status {response.status_code}, Response {response.text}")

            print(f"Sent traffic status: {traffic_status['status']} to Central API")
        except Exception as e:
            print(f"Error updating traffic status: {e}")
        time.sleep(10)  # Actualizar cada 10 segundos

@app.route('/traffic_status', methods=['GET'])
def get_traffic_status():
    return jsonify({"traffic_status": traffic_status["status"]})

@app.route('/update_city', methods=['POST'])
def update_city():
    data = request.json
    city = data.get('city')
    api_key = data.get('api_key')
    if city:
        CONFIG['CITY'] = city
    if api_key is not None:
        CONFIG['APICTC'] = api_key
    save_config()
    return jsonify({"message": "Configuration updated"})

if __name__ == "__main__":
    # Iniciar el hilo para actualizar el estado del tráfico
    threading.Thread(target=fetch_temperature_and_update_central).start()
    # Iniciar el servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5001)