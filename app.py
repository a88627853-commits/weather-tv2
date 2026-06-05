<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<title>Weather TV</title>

<style>
body {
    margin: 0;
    background: black;
    color: white;
    font-family: Arial;
    overflow: hidden;
}

#tv {
    width: 960px;
    height: 960px;
    margin: auto;
    background: #111;
    position: relative;
    overflow: hidden;
}

/* 🗺️ MAPA */
#map {
    position: absolute;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.85;
}

/* 📍 MARKERY */
.marker {
    position: absolute;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 6px black;
}

.marker.RED { background: red; }
.marker.YELLOW { background: orange; }
.marker.MEDIUM { background: gold; }
.marker.LOW { background: lime; }

/* 📊 LISTA */
.city {
    font-size: 12px;
    padding: 2px;
    border-bottom: 1px solid #222;
}

/* 📉 TICKER */
#ticker {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: black;
    color: lime;
}

#ticker span {
    display: inline-block;
    padding-left: 100%;
    animation: scroll 25s linear infinite;
}

@keyframes scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-100%); }
}

/* 🚨 EAS */
#eas {
    position: fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    display:none;
    justify-content:center;
    align-items:center;
    font-size:42px;
    text-align:center;
    z-index:999;
    white-space: pre-line;
}

/* FULLSCREEN */
button {
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 10;
}
</style>
</head>

<body>

<button onclick="document.documentElement.requestFullscreen()">FULLSCREEN</button>

<div id="tv">
    <img id="map" src="map.png">
</div>

<div id="ticker"><span>ŁADOWANIE DANYCH...</span></div>

<div id="eas"></div>

<script>

/* 🌍 KALIBRACJA MAPY POLSKI */
const MAP = {
    latMin: 49.0,
    latMax: 55.2,
    lonMin: 14.0,
    lonMax: 24.5
};

function geoToXY(lat, lon) {
    const map = document.getElementById("map");

    const w = map.clientWidth;
    const h = map.clientHeight;

    const x = ((lon - MAP.lonMin) / (MAP.lonMax - MAP.lonMin)) * w;
    const y = ((MAP.latMax - lat) / (MAP.latMax - MAP.latMin)) * h;

    return {x, y};
}

/* 🎨 kolor alertu */
function getColor(alert){
    return alert || "LOW";
}

/* 📍 RYSOWANIE MARKERÓW */
function drawMarkers(cities){
    const tv = document.getElementById("tv");

    document.querySelectorAll(".marker").forEach(m => m.remove());

    cities.forEach((c)=>{

        if(!c.lat || !c.lon) return;

        let pos = geoToXY(c.lat, c.lon);

        let m = document.createElement("div");
        m.className = "marker " + getColor(c.alert);

        m.style.left = pos.x + "px";
        m.style.top = pos.y + "px";

        tv.appendChild(m);
    });
}

/* 🚨 EAS SYSTEM */
function checkEAS(){
    fetch("/eas/global")
    .then(r=>r.json())
    .then(e=>{

        let box = document.getElementById("eas");

        if(e.level==="RED"){
            box.style.display="flex";
            box.style.background="red";
            box.innerText="🚨 ALERT KRYTYCZNY\n" + e.cities.join(", ");
        }

        else if(e.level==="YELLOW"){
            box.style.display="flex";
            box.style.background="orange";
            box.innerText="⚠️ OSTRZEŻENIE\n" + e.cities.join(", ");
        }

        else {
            box.style.display="none";
        }
    });
}

/* 📊 LOAD DATA */
function load(){
    fetch("/data")
    .then(r=>r.json())
    .then(d=>{

        checkEAS();

        /* TICKER */
        document.querySelector("#ticker span").innerText =
            d.cities.map(c =>
                `${c.name}: ${c.current?.temperature_2m ?? "?"}°C`
            ).join(" | ");

        /* MAPA */
        drawMarkers(d.cities);
    });
}

setInterval(load, 30000);
load();

</script>

</body>
</html>
