from flask import Flask, jsonify, send_from_directory
import requests
import time

app = Flask(__name__)

API_KEY = "e20abb7bb600400fb2c134205260506"  # 🔴 tylko backend

CITIES = [
    "Zakopane","Przemyśl","Bielsko-Biała","Kraków","Katowice",
    "Zamość","Kielce","Częstochowa","Lublin","Wrocław",
    "Radom","Łódź","Zielona Góra","Warszawa","Poznań",
    "Płock","Gorzów Wlkp.","Białystok","Szczecin","Olsztyn",
    "Augustów","Suwałki","Świnoujście","Kołobrzeg","Koszalin",
    "Gdańsk","Gdynia"
]

CACHE = None
CACHE_TIME = 0
CACHE_TTL = 60


def fetch_city(city):
    url = "http://api.weatherapi.com/v1/forecast.json"

    params = {
        "key": API_KEY,
        "q": city,
        "days": 1,
        "aqi": "no",
        "alerts": "no"
    }

    try:
        r = requests.get(url, params=params, timeout=10).json()

        cur = r.get("current", {})

        return {
            "name": city,
            "temp": cur.get("temp_c"),
            "feels": cur.get("feelslike_c"),
            "wind": cur.get("wind_kph"),
            "humidity": cur.get("humidity"),
            "pressure": cur.get("pressure_mb"),
            "cloud": cur.get("cloud"),
            "vis": cur.get("vis_km"),
            "code": cur.get("condition", {}).get("code"),
            "text": cur.get("condition", {}).get("text"),
            "icon": cur.get("condition", {}).get("icon")
        }

    except:
        return {
            "name": city,
            "temp": None,
            "wind": None,
            "humidity": None
        }


def get_data():
    global CACHE, CACHE_TIME

    now = time.time()

    if CACHE is None or (now - CACHE_TIME) > CACHE_TTL:
        CACHE = [fetch_city(c) for c in CITIES]
        CACHE_TIME = now

    return CACHE


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/data")
def data():
    return jsonify({
        "cities": get_data()
    })


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
