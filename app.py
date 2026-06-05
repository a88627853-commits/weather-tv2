from flask import Flask, jsonify, send_from_directory
import requests
import time

app = Flask(__name__)

API_KEY = "e20abb7bb600400fb2c134205260506"  # backend only (nie dotykam 😄)

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


# =========================
# WEATHER FETCH (STABILNY)
# =========================
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
                "code": None
            }

        current = data.get("current") or {}
        cond = current.get("condition") or {}

        icon = cond.get("icon")
        if icon and icon.startswith("//"):
            icon = "https:" + icon

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
            "code": cond.get("code")
        }

    except Exception:
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
            "code": None
        }


# =========================
# CACHE (ANTI-LAG + RATE LIMIT SAFE)
# =========================
def get_data():
    global CACHE, CACHE_TIME

    now = time.time()

    if CACHE is None or (now - CACHE_TIME) > CACHE_TTL:
        new_cache = []

        for c in CITIES:
            new_cache.append(fetch_city(c))
            time.sleep(0.12)  # chroni API przed limitem

        CACHE = new_cache
        CACHE_TIME = now

    return CACHE


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/data")
def data():
    return jsonify({"cities": get_data()})


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)


# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
