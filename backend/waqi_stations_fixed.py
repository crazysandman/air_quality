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

    print(f"Abrufen der Stations-Bounds...")
    bounds_response = requests.get(bounds_url)
    
    if bounds_response.status_code != 200:
        raise Exception(f"HTTP Error beim Bounds-Abruf: {bounds_response.status_code}")
    
    bounds_data = bounds_response.json()

    if bounds_data["status"] != "ok":
        raise Exception(f"Bounds API Error: {bounds_data.get('data', 'Unknown error')}")

    print(f"Gefunden: {len(bounds_data.get('data', []))} Stationen in der Region")
    
    features = []
    successful_stations = 0
    failed_stations = 0

    for station in bounds_data.get("data", []):
        uid = station.get("uid")
        if not uid:
            continue

        try:
            # Detaildaten pro Station abrufen
            feed_url = f"https://api.waqi.info/feed/@{uid}/?token={WAQI_TOKEN}"
            feed_response = requests.get(feed_url, timeout=10)
            
            if feed_response.status_code != 200:
                failed_stations += 1
                print(f"HTTP Error für Station {uid}: {feed_response.status_code}")
                continue
                
            feed_data = feed_response.json()

            if feed_data["status"] != "ok":
                failed_stations += 1
                # Nicht jede fehlgeschlagene Station loggen, das wird zu viel Output
                continue

            d = feed_data["data"]

            # Prüfen ob die Station gültige Daten hat
            if not d.get("city") or not d.get("city", {}).get("geo"):
                failed_stations += 1
                continue

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
                    "no2": d.get("iaqi", {}).get("no2", {}).get("v"),
                    "o3": d.get("iaqi", {}).get("o3", {}).get("v"),
                    "co": d.get("iaqi", {}).get("co", {}).get("v"),
                    "so2": d.get("iaqi", {}).get("so2", {}).get("v"),
                    "timestamp": timestamp.isoformat()
                }
            })
            successful_stations += 1

        except Exception as e:
            failed_stations += 1
            continue

    print(f"Verarbeitung abgeschlossen: {successful_stations} erfolgreich, {failed_stations} fehlgeschlagen")
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "total_stations": len(features),
            "successful_stations": successful_stations,
            "failed_stations": failed_stations,
            "region": "Berlin"
        }
    }
