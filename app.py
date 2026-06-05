from flask import Flask, jsonify, send_from_directory
import requests
import time

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


CACHE = None
CACHE_TIME = 0
CACHE_TTL = 60


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
            "pressure_msl"
        ]
    }

    r = requests.get(url, params=params, timeout=10).json()
    h = r.get("hourly", {})

    def first(arr):
        return arr[0] if isinstance(arr, list) and len(arr) > 0 else None

    return {
        "name": NAMES[i],
        "lat": LAT[i],
        "lon": LON[i],

        # 🔥 NORMALIZACJA (KLUCZ SYSTEMU)
        "temp": first(h.get("temperature_2m")),
        "feels": first(h.get("apparent_temperature")),
        "humidity": first(h.get("relative_humidity_2m")),
        "wind": first(h.get("wind_speed_10m")),
        "cloud": first(h.get("cloud_cover")),
        "vis": first(h.get("visibility")),
        "pressure": first(h.get("pressure_msl")),
        "code": first(h.get("weather_code")),

        "alert": "OK"
    }


def get_data():
    global CACHE, CACHE_TIME

    now = time.time()

    if CACHE is None or (now - CACHE_TIME) > CACHE_TTL:
        CACHE = [fetch_city(i) for i in range(len(NAMES))]
        CACHE_TIME = now

    return CACHE


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/map.png")
def map():
    return send_from_directory(".", "map.png")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)


@app.route("/data")
def data():
    return jsonify({
        "cities": get_data()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
