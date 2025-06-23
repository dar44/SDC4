import requests
import time
import os
from flask import Flask, jsonify, request
import variablesGlobales as vg
import threading
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(filename='auditoriaEC.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# Variables globales para OpenWeather
IP = vg.IP_API
urlUpdate = f"http://{IP}:5000/update-traffic"
traffic_status = {"status": "OK"}
current_temperature = 0.0

def _fetch_temperature():
    """Consults OpenWeather and updates ``traffic_status``."""
    CITYNAME = vg.CONFIG.get('CITY', 'Alicante,ES')
    api_key = vg.CONFIG.get('APICTC', '')

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
        logging.info(
            f"Fetched temperature for {CITYNAME}: {temp:.2f}C, status {traffic_status['status']}"
        )
        return CITYNAME, temp
    except Exception as e:
        # Ante cualquier error se marca el estado como KO para avisar a la central
        traffic_status["status"] = "KO"
        logging.error(f"Error fetching temperature for {CITYNAME}: {e}")
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
    log_msg = (
        f"POST to {urlUpdate}: Status {resp.status_code}, Response {resp.text}; "
        f"city={city}, temp={temperature:.2f}C"
    )
    print(log_msg)
    logging.info(log_msg)

def fetch_temperature_and_update_central():
    global current_temperature
    while True:
        try:
            city, temp = _fetch_temperature()
            current_temperature = temp
            _send_status(city, temp)
            log_msg = (
                f"Sent traffic status: {traffic_status['status']} to Central API, "
                f"city={city}, temp={temp:.2f}C"
            )
            print(log_msg)
            logging.info(log_msg)
        except Exception as e:
            print(f"Error updating traffic status: {e}")
        time.sleep(10)  # Actualizar cada 10 segundos

@app.route('/traffic_status', methods=['GET'])
def get_traffic_status():
    return jsonify({
        "traffic_status": traffic_status["status"],
        "city": vg.CONFIG.get("CITY", ""),
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
        logging.info(
            f"Manual status update: city={city}, temp={temp:.2f}C, status={traffic_status['status']}"
        )
        return jsonify({"message": "Traffic status sent", "status": traffic_status["status"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/update_city', methods=['POST'])
def update_city():
    data = request.get_json(force=True, silent=True) or {}
    city = data.get('city')
    logging.info(f"Received update_city request: city={city}")
    if not city:
        return jsonify({"error": "city is required"}), 400

    vg.CONFIG['CITY'] = city
    vg.CITY = city
    vg.save_config()

    global current_temperature
    try:
        city_name, temp = _fetch_temperature()
        current_temperature = temp
    except Exception:
        city_name = city
        temp = -1.0

    _send_status(city_name, temp)
    logging.info(
        f"Updated city to {city_name}, temp={temp:.2f}C, status={traffic_status['status']}"
    )
    return jsonify({
        "message": "City updated",
        "status": traffic_status["status"],
        "city": city_name,
        "temperature": round(temp, 2)
    })

@app.route('/update_api_key', methods=['POST'])
def update_api_key():
    """Update only the OpenWeather API key."""
    data = request.get_json(force=True, silent=True) or {}
    api_key = data.get('api_key')
    logging.info(f"Received update_api_key request: api_key={'provided' if api_key else 'none'}")
    if not api_key:
        return jsonify({"error": "api_key is required"}), 400

    vg.CONFIG['APICTC'] = api_key
    vg.APICTC = api_key
    vg.save_config()

    global current_temperature
    try:
        city_name, temp = _fetch_temperature()
        current_temperature = temp
    except Exception:
        city_name = vg.CONFIG.get('CITY', 'Alicante,ES')
        temp = -1.0

    _send_status(city_name, temp)
    logging.info(
        f"Updated API key, city={city_name}, temp={temp:.2f}C, status={traffic_status['status']}"
    )
    return jsonify({
        "message": "API key updated",
        "status": traffic_status["status"],
        "city": city_name,
        "temperature": round(temp, 2)
    })


if __name__ == "__main__":
    try:
        # Iniciar el hilo para actualizar el estado del tráfico
        threading.Thread(target=fetch_temperature_and_update_central, daemon=True).start()
        # Iniciar el servidor Flask
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("CTC detenido por el usuario.")