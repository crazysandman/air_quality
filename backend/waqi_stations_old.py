import requests
import os
from datetime import datetime

WAQI_TOKEN = os.getenv("WAQI_API_TOKEN")

# Berlin-Umgebung als grobes Bounding Box (ca. 15x15 km)
BERLIN_BOUNDS = {
    "lat1": 52.40,
    "lat2": 52.60,
    "lon1": 13.20,
    "lon2": 13.60,
}


def fetch_berlin_stations():
    bounds_url = (
        f"https://api.waqi.info/map/bounds/"
        f"?latlng={BERLIN_BOUNDS['lat1']},{BERLIN_BOUNDS['lon1']},"
        f"{BERLIN_BOUNDS['lat2']},{BERLIN_BOUNDS['lon2']}&token={WAQI_TOKEN}"
    )

    bounds_response = requests.get(bounds_url)
    bounds_data = bounds_response.json()

    if bounds_data["status"] != "ok":
        raise Exception("Fehler beim Abrufen der Bound-Daten")

    features = []

    for station in bounds_data.get("data", []):
        uid = station.get("uid")
        if not uid:
            continue

        # Detaildaten pro Station abrufen
        feed_url = f"https://api.waqi.info/feed/@{uid}/?token={WAQI_TOKEN}"
        feed_response = requests.get(feed_url)
        feed_data = feed_response.json()

        if feed_data["status"] != "ok":
            print(f"Station {uid} übersprungen: {feed_data.get('data', 'Unbekannter Fehler')}")
            continue
            print(f"Station {uid} übersprungen: {feed_data.get('data', 'Unbekannter Fehler')}")
            continue

        d = feed_data["data"]

        try:
            lat = float(d["city"]["geo"][0])
            lon = float(d["city"]["geo"][1])
            timestamp = datetime.strptime(d["time"]["s"], "%Y-%m-%d %H:%M:%S")

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "uid": uid,
                    "station": d["city"]["name"],
                    "aqi": d.get("aqi"),
                    "pm25": d.get("iaqi", {}).get("pm25", {}).get("v"),
                    "pm10": d.get("iaqi", {}).get("pm10", {}).get("v"),
                    "timestamp": timestamp.isoformat()
                }
            })

        except Exception as e:
            print(f"Fehler bei Station {uid}: {e}")
            continue

    return {
        "type": "FeatureCollection",
        "features": features
    }