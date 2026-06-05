from flask import Flask, jsonify, send_from_directory
import requests
import time

app = Flask(__name__)

API_KEY = "e20abb7bb600400fb2c134205260506"  # backend only

CITIES = [
    "Zakopane","Przemyśl","Bielsko-Biała","Kraków","Katowice",
    "Zamość","Kielce","Częstochowa","Lublin","Wrocław",
    "Radom","Łódź","Zielona Góra","Warszawa","Poznań",
    "Płock","Gorzów Wlkp.","Białystok","Szczecin","Olsztyn",
    "Augustów","Suwałki","Świnoujście","Kołobrzeg","Koszalin",
    "Gdańsk","Gdynia"
]

# 🔥 FIX: fallback geolokalizacji (WeatherAPI czasem nie daje lat/lon)
CITY_GEO = {
    "Wrocław": (51.107883, 17.038538),
    "Łódź": (51.759247, 19.455982),
    "Poznań": (52.406376, 16.925167),
    "Płock": (52.546345, 19.706535),
    "Białystok": (53.132488, 23.168840),
    "Suwałki": (54.099941, 22.931711),
    "Kołobrzeg": (54.181679, 15.569580),
    "Przemyśl": (49.783699, 22.768030)
}

CACHE = None
CACHE_TIME = 0
CACHE_TTL = 60


def fetch_city(city):
    url = "https://api.weatherapi.com/v1/forecast.json"

    params = {
        "key": API_KEY,
        "q": city,
        "days": 1,
        "aqi": "no",
        "alerts": "no"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if "error" in data:
            lat, lon = CITY_GEO.get(city, (None, None))

            return {
                "name": city,
                "temp": None,
                "wind": None,
                "humidity": None,
                "pressure": None,
                "cloud": None,
                "feels": None,
                "vis": None,
                "text": None,
                "icon": None,
                "code": -1,
                "lat": lat,
                "lon": lon
            }

        current = data.get("current") or {}
        cond = current.get("condition") or {}
        location = data.get("location") or {}

        icon = cond.get("icon")
        if icon and icon.startswith("//"):
            icon = "https:" + icon

        lat = location.get("lat")
        lon = location.get("lon")

        # 🔥 FALLBACK jeśli API nie dało współrzędnych
        if not lat or not lon:
            lat, lon = CITY_GEO.get(city, (None, None))

        return {
            "name": city,
            "temp": current.get("temp_c"),
            "wind": current.get("wind_kph"),
            "humidity": current.get("humidity"),
            "pressure": current.get("pressure_mb"),
            "cloud": current.get("cloud"),
            "feels": current.get("feelslike_c"),
            "vis": current.get("vis_km"),
            "text": cond.get("text"),
            "icon": icon,
            "code": cond.get("code", -1),
            "lat": lat,
            "lon": lon
        }

    except Exception:
        lat, lon = CITY_GEO.get(city, (None, None))

        return {
            "name": city,
            "temp": None,
            "wind": None,
            "humidity": None,
            "pressure": None,
            "cloud": None,
            "feels": None,
            "vis": None,
            "text": None,
            "icon": None,
            "code": -1,
            "lat": lat,
            "lon": lon
        }


def get_data():
    global CACHE, CACHE_TIME

    now = time.time()

    if CACHE is None or (now - CACHE_TIME) > CACHE_TTL:
        new_cache = []

        for c in CITIES:
            new_cache.append(fetch_city(c))
            time.sleep(0.12)

        CACHE = new_cache
        CACHE_TIME = now

    return CACHE


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/data")
def data():
    return jsonify({"cities": get_data()})


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
