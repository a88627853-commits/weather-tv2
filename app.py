from flask import Flask, jsonify, send_from_directory, request
import requests
import threading
import time
import os

app = Flask(__name__)

LAT = [49.299, 50.0413, 49.785, 50.0614, 50.2597, 50.7231, 50.8703,
       50.7965, 51.2506, 51.4025, 52.2298, 51.7706, 51.9355, 52.4069,
       52.5468, 52.7337, 53.1333, 53.3833, 53.7838, 53.8432, 54.1118,
       53.9105, 54.1756, 54.1944, 54.3523, 54.5189, 54.7909]

LON = [19.9489, 21.999, 22.7673, 19.9366, 19.0217, 23.252, 20.6275,
       19.1241, 22.5701, 21.1471, 21.0118, 19.4739, 15.5064, 16.9299,
       19.7064, 15.225, 23.1643, 14.6333, 20.4927, 22.9798, 22.9309,
       14.2471, 15.5834, 16.1722, 18.6491, 18.5319, 18.4009]

NAMES = ["Zakopane","Przemyśl","Bielsko-Biała","Kraków","Katowice",
         "Zamość","Kielce","Częstochowa","Lublin","Wrocław",
         "Radom","Łódź","Zielona Góra","Warszawa","Poznań",
         "Płock","Gorzów Wlkp.","Białystok","Szczecin","Olsztyn",
         "Augustów","Suwałki","Świnoujście","Kołobrzeg","Koszalin",
         "Gdańsk","Gdynia"]

# 🔴 EAS STATE
EAS_ACTIVE = False
EAS_END_TIME = 0


# =========================
# WEATHER
# =========================
def get_city(i):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LAT[i],
        "longitude": LON[i],
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "dew_point_2m",
            "apparent_temperature",
            "weather_code",
            "pressure_msl",
            "cloud_cover",
            "wind_speed_10m",
            "visibility",
            "is_day"
        ],
        "hourly": [
            "wind_speed_10m",
            "wind_speed_80m",
            "wind_gusts_10m",
            "precipitation_probability",
            "precipitation",
            "snowfall",
            "sunshine_duration",
            "cape"
        ],
        "timezone": "Europe/Warsaw"
    }

    try:
        r = requests.get(url, params=params, timeout=10).json()
    except:
        return {"name": NAMES[i], "error": True}

    return {
        "name": NAMES[i],
        "lat": LAT[i],
        "lon": LON[i],
        "current": r.get("current", {}),
        "hourly": r.get("hourly", {}),
        "alert": "EAS" if EAS_ACTIVE else "OK"
    }


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/data")
def data():
    return jsonify({
        "eas": EAS_ACTIVE,
        "cities": [get_city(i) for i in range(len(NAMES))],
        "system_info": "Weather-TV system built step-by-step over multiple hours (stream build mode)"
    })


# =========================
# ESP32 TRIGGER
# =========================
@app.route("/esp32/eas_test", methods=["POST"])
def esp32_eas():
    global EAS_ACTIVE, EAS_END_TIME

    print("🔴 ESP32 TRIGGER → EAS TEST MODE")

    EAS_ACTIVE = True
    EAS_END_TIME = time.time() + 60

    return jsonify({"status": "EAS TEST ACTIVE", "duration": 60})


# =========================
# EAS WATCHER
# =========================
def eas_watcher():
    global EAS_ACTIVE

    while True:
        if EAS_ACTIVE and time.time() > EAS_END_TIME:
            print("🟢 EAS STOP")
            EAS_ACTIVE = False

        time.sleep(1)


# =========================
# START
# =========================
threading.Thread(target=eas_watcher, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
