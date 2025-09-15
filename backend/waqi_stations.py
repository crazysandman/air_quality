import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
current_dir = Path(__file__).parent
load_dotenv(current_dir / ".env")

WAQI_TOKEN = os.getenv("WAQI_API_TOKEN")

# Berlin-Umgebung als erweiterte Bounding Box (ca. 25x25 km)
BERLIN_BOUNDS = {
    "lat1": 52.35,   # Weiter südlich
    "lat2": 52.65,   # Weiter nördlich  
    "lon1": 13.10,   # Weiter westlich
    "lon2": 13.70,   # Weiter östlich
}


def fetch_berlin_stations():
    # Method 1: Bounds API für Berlin Region
    bounds_url = (
        f"https://api.waqi.info/map/bounds/"
        f"?latlng={BERLIN_BOUNDS['lat1']},{BERLIN_BOUNDS['lon1']},"
        f"{BERLIN_BOUNDS['lat2']},{BERLIN_BOUNDS['lon2']}&token={WAQI_TOKEN}"
    )

    # Method 2: Search API für spezifische Berlin Stationen
    search_terms = ["berlin", "germany"]
    search_url = f"https://api.waqi.info/search/?token={WAQI_TOKEN}&keyword=berlin"

    all_stations = {}  # Dictionary um Duplikate zu vermeiden (key = uid)

    try:
        # 1. Bounds API Abfrage
        bounds_response = requests.get(bounds_url, timeout=30)
        
        if bounds_response.status_code == 200:
            bounds_data = bounds_response.json()
            if bounds_data["status"] == "ok":
                for station in bounds_data.get("data", []):
                    uid = station.get("uid")
                    if uid and station.get("lat") and station.get("lon"):
                        all_stations[uid] = station

        # 2. Search API Abfrage (zusätzliche Stationen)
        try:
            search_response = requests.get(search_url, timeout=30)
            if search_response.status_code == 200:
                search_data = search_response.json()
                if search_data["status"] == "ok":
                    for station in search_data.get("data", []):
                        uid = station.get("uid")
                        # Füge nur Stationen in Berlin-Region hinzu
                        if (uid and uid not in all_stations and 
                            station.get("station", {}).get("geo") and
                            len(station["station"]["geo"]) >= 2):
                            
                            lat = float(station["station"]["geo"][0])
                            lon = float(station["station"]["geo"][1])
                            
                            # Prüfe ob in erweiterter Berlin-Region
                            if (BERLIN_BOUNDS["lat1"] <= lat <= BERLIN_BOUNDS["lat2"] and 
                                BERLIN_BOUNDS["lon1"] <= lon <= BERLIN_BOUNDS["lon2"]):
                                
                                # Konvertiere Search-Format zu Bounds-Format
                                converted_station = {
                                    "uid": uid,
                                    "lat": lat,
                                    "lon": lon,
                                    "aqi": station.get("aqi"),
                                    "station": {
                                        "name": station.get("station", {}).get("name", "Unknown"),
                                        "time": station.get("station", {}).get("time", "")
                                    }
                                }
                                all_stations[uid] = converted_station
        except Exception as e:
            print(f"Search API error (continuing with bounds data): {e}")

        # Konvertiere zu GeoJSON Features
        features = []
        for uid, station in all_stations.items():
            try:
                lat = float(station.get("lat", 0))
                lon = float(station.get("lon", 0))
                
                if lat == 0 or lon == 0:
                    continue
                    
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "uid": uid,
                        "station": station.get("station", "Unknown"),
                        "aqi": station.get("aqi"),
                        "timestamp": datetime.now().isoformat(),
                        "source": "bounds_and_search_api"
                    }
                })

            except Exception as e:
                continue
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "total_stations": len(features),
                "region": "Berlin (Extended)",
                "note": "Data from bounds + search API - for detailed station data use /waqi/berlin-stations/detailed",
                "search_methods": ["bounds_api", "search_api"]
            }
        }
        
    except Exception as e:
        # Bei Fehlern eine leere FeatureCollection zurückgeben
        return {
            "type": "FeatureCollection",
            "features": [],
            "properties": {
                "error": str(e),
                "total_stations": 0,
                "region": "Berlin"
            }
        }


def fetch_berlin_stations_detailed():
    """
    Holt detaillierte Daten für alle Berlin Stationen mit erweiterten Schadstoffen und Wetterdaten
    """
    token = WAQI_TOKEN
    if not token:
        raise ValueError("WAQI_TOKEN is required")
    
    # Hole zunächst die Basis-Stationen
    basic_stations = fetch_berlin_stations()
    
    if not basic_stations or "features" not in basic_stations:
        return {"type": "FeatureCollection", "features": []}
    
    detailed_features = []
    
    for station in basic_stations["features"]:
        station_uid = station.get("properties", {}).get("uid")
        if not station_uid:
            continue
            
        try:
            # Hole detaillierte Daten für diese Station
            station_url = f"https://api.waqi.info/feed/@{station_uid}/?token={token}"
            response = requests.get(station_url, timeout=10)
            
            if response.status_code == 200:
                station_data = response.json()
                
                if station_data.get("status") == "ok" and "data" in station_data:
                    data = station_data["data"]
                    
                    # Erweiterte Properties mit detaillierten Daten
                    enhanced_properties = {
                        "uid": station_uid,
                        "name": data.get("city", {}).get("name", "Unknown"),
                        "url": data.get("city", {}).get("url", ""),
                        "aqi": data.get("aqi"),
                        "time": data.get("time", {}).get("s"),
                        
                        # Schadstoffe aus iaqi (individual AQI)
                        "pm25": data.get("iaqi", {}).get("pm25", {}).get("v"),
                        "pm10": data.get("iaqi", {}).get("pm10", {}).get("v"),
                        "no2": data.get("iaqi", {}).get("no2", {}).get("v"),
                        "o3": data.get("iaqi", {}).get("o3", {}).get("v"),
                        "co": data.get("iaqi", {}).get("co", {}).get("v"),
                        "so2": data.get("iaqi", {}).get("so2", {}).get("v"),
                        
                        # Wetterdaten
                        "temperature": data.get("iaqi", {}).get("t", {}).get("v"),
                        "pressure": data.get("iaqi", {}).get("p", {}).get("v"),
                        "humidity": data.get("iaqi", {}).get("h", {}).get("v"),
                        "wind_speed": data.get("iaqi", {}).get("w", {}).get("v"),
                        
                        # Quellenangaben
                        "attributions": data.get("attributions", [])
                    }
                    
                    # Erstelle enhanced Feature
                    enhanced_feature = {
                        "type": "Feature",
                        "geometry": station["geometry"],  # Verwende Original-Koordinaten
                        "properties": enhanced_properties
                    }
                    
                    detailed_features.append(enhanced_feature)
                    
        except Exception as e:
            print(f"Error fetching detailed data for station {station_uid}: {e}")
            # Fallback: verwende Basis-Station
            detailed_features.append(station)
            continue
    
    print(f"Enhanced {len(detailed_features)} stations with detailed data")
    
    return {
        "type": "FeatureCollection",
        "features": detailed_features
    }
