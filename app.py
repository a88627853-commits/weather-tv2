from flask import Flask, jsonify, send_from_directory
import requests

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

def calculate_alert(cur, h):
    wind = h.get("wind_speed_10m", [0])[0]
    gust = h.get("wind_gusts_10m", [0])[0]
    rain = h.get("precipitation_probability", [0])[0]
    snow = h.get("snow_depth", [0])[0]
    code = cur.get("weather_code", 0)

    score = 0
    if wind > 20: score += 2
    elif wind > 12: score += 1

    if gust > 25: score += 2

    if rain > 70: score += 2
    elif rain > 40: score += 1

    if snow > 5: score += 2
    if code >= 95: score += 3

    if score >= 6: return "EXTREME"
    if score >= 4: return "HIGH"
    return "LOW"


def get_city(i):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LAT[i],
        "longitude": LON[i],
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "cloud_cover",
            "pressure_msl",
            "surface_pressure",
            "is_day",
            "wind_speed_10m",
            "visibility"
        ],
        "hourly": [
            "wind_speed_10m",
            "wind_speed_80m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "precipitation_probability",
            "precipitation",
            "snow_depth",
            "uv_index",
            "uv_index_clear_sky",
            "sunshine_duration"
        ],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "sunrise",
            "sunset"
        ],
        "timezone": "Europe/Warsaw"
    }

    r = requests.get(url, params=params, timeout=10).json()

    cur = r.get("current", {})
    h = r.get("hourly", {})
    d = r.get("daily", {})

    return {
        "name": NAMES[i],
        "lat": LAT[i],
        "lon": LON[i],
        "current": cur,
        "hourly": h,
        "daily": d,
        "alert": calculate_alert(cur, h)
    }


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/data")
def data():
    return jsonify({"cities": [get_city(i) for i in range(len(NAMES))]})


@app.route("/eas/global")
def eas_global():
    cities = [get_city(i) for i in range(len(NAMES))]

    extreme = [c for c in cities if c["alert"] == "EXTREME"]
    high = [c for c in cities if c["alert"] == "HIGH"]

    if extreme:
        return jsonify({"level": "RED", "cities": [c["name"] for c in extreme]})

    if high:
        return jsonify({"level": "YELLOW", "cities": [c["name"] for c in high]})

    return jsonify({"level": "GREEN", "cities": []})


if __name__ == "__main__":
    app.run(host="0.0.0.0")
