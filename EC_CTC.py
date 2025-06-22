import requests
import time
import os
from flask import Flask, jsonify, request
from variablesGlobales import CONFIG, IP_API, save_config
import threading
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Variables globales para OpenWeather
IP = IP_API
urlUpdate = f"http://{IP}:5000/update-traffic"
traffic_status = {"status": "OK"}
current_temperature = 0.0

def _fetch_temperature():
    """Consults OpenWeather and updates ``traffic_status``."""
    CITYNAME = CONFIG.get('CITY', 'Alicante,ES')
    api_key = CONFIG.get('APICTC', '')

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={CITYNAME}&appid={api_key}"
    )
    #response = requests.get(url)
    #data = response.json()
    #temp = data['main']['temp'] - 273.15
    #traffic_status["status"] = "KO" if temp < 0 else "OK"
    #return CITYNAME, temp
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temp = data['main']['temp'] - 273.15
        traffic_status["status"] = "KO" if temp < 0 else "OK"
        return CITYNAME, temp
    except Exception:
        # Ante cualquier error se marca el estado como KO para avisar a la central
        traffic_status["status"] = "KO"
        raise


def _send_status(city, temperature):
    """Sends the status to the central API."""
    resp = requests.post(
        urlUpdate,
        json={
            "status": traffic_status["status"],
            "city": city,
            "temperature": temperature,
        },
    )
    print(
        f"POST to {urlUpdate}: Status {resp.status_code}, Response {resp.text}"
    )
    
def fetch_temperature_and_update_central():
    global current_temperature
    while True:
        try:
            city, temp = _fetch_temperature()
            current_temperature = temp
            _send_status(city, temp)
            print(
                f"Sent traffic status: {traffic_status['status']} to Central API"
            )
        except Exception as e:
            print(f"Error updating traffic status: {e}")
        time.sleep(10)  # Actualizar cada 10 segundos

@app.route('/traffic_status', methods=['GET'])
def get_traffic_status():
    return jsonify({
        "traffic_status": traffic_status["status"],
        "city": CONFIG.get("CITY", ""),
        "temperature": round(current_temperature, 2)
    })

@app.route('/send_status', methods=['POST'])
def send_status_route():
    """Force an immediate status update to the central API."""
    try:
        city, temp = _fetch_temperature()
        global current_temperature
        current_temperature = temp
        _send_status(city, temp)
        return jsonify({"message": "Traffic status sent", "status": traffic_status["status"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
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
    global current_temperature
    try:
        city_name, temp = _fetch_temperature()
        current_temperature = temp
    except Exception:
        city_name = city if city else CONFIG.get('CITY', 'Alicante,ES')
        temp = 0.0
    _send_status(city_name, temp)
    return jsonify({
        "message": "Configuration updated",
        "status": traffic_status["status"],
        "city": city_name,
        "temperature": round(temp, 2)
    })


if __name__ == "__main__":
    # Iniciar el hilo para actualizar el estado del tráfico
    threading.Thread(target=fetch_temperature_and_update_central).start()
    # Iniciar el servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5001)