from flask import Flask, jsonify, send_from_directory
import requests
import time
import threading

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

CACHE = []
CACHE_TTL = 60

EAS_ACTIVE = False
EAS_END = 0


# =========================
# FIXED FETCH (ONLY HOURLY + DAILY STYLE DATA)
# =========================
def fetch_city(i):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LAT[i],
        "longitude": LON[i],
        "timezone": "Europe/Warsaw",

        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "wind_speed_10m",
            "cloud_cover",
            "weather_code",
            "visibility",
            "pressure_msl",
            "surface_pressure"
        ],

        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "sunrise",
            "sunset",
            "weather_code"
        ]
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        return {
            "name": NAMES[i],
            "lat": LAT[i],
            "lon": LON[i],
            "hourly": data.get("hourly", {}),
            "daily": data.get("daily", {}),
            "alert": "EAS" if EAS_ACTIVE else "OK"
        }

    except:
        return {
            "name": NAMES[i],
            "lat": LAT[i],
            "lon": LON[i],
            "hourly": {},
            "daily": {},
            "alert": "OK"
        }


# =========================
# CACHE
# =========================
def build_cache():
    global CACHE
    CACHE = [fetch_city(i) for i in range(len(NAMES))]


def update_cache():
    while True:
        build_cache()
        time.sleep(CACHE_TTL)


# =========================
# EAS
# =========================
def eas_loop():
    global EAS_ACTIVE
    while True:
        if EAS_ACTIVE and time.time() > EAS_END:
            EAS_ACTIVE = False
        time.sleep(1)


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/map.png")
def map():
    return send_from_directory(".", "map.png")


@app.route("/data")
def data():
    return jsonify({
        "eas": EAS_ACTIVE,
        "cities": CACHE
    })


@app.route("/esp32/eas_test", methods=["POST"])
def eas():
    global EAS_ACTIVE, EAS_END
    EAS_ACTIVE = True
    EAS_END = time.time() + 60
    return {"ok": True}


# =========================
# START
# =========================
build_cache()

threading.Thread(target=update_cache, daemon=True).start()
threading.Thread(target=eas_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
