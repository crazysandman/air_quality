import requests
from db import SessionLocal
from models import SensorData
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from datetime import datetime

URL = "https://data.sensor.community/airrohr/v1/filter/box=52.3,13.0,52.7,13.6"
HEADERS = {"User-Agent": "air-quality-iot-bht/1.0 (jakob1997@t-online.de)"}

def fetch_and_store():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        data = response.json()
    except Exception as e:
        print("Fehler beim Abruf:", e)
        return

    db = SessionLocal()
    inserted = 0

    for entry in data:
        lat = entry.get("location", {}).get("latitude")
        lon = entry.get("location", {}).get("longitude")
        sensor_id = entry.get("sensor", {}).get("id")
        timestamp = entry.get("timestamp")

        if not all([lat, lon, sensor_id, timestamp]):
            continue

        pm25 = None
        temperature = None

        for val in entry.get("sensordatavalues", []):
            if val["value_type"] == "P2":
                pm25 = float(val["value"])
            elif val["value_type"] == "temperature":
                temperature = float(val["value"])

        if not any([pm25, temperature]):
            continue

        point = from_shape(Point(lon, lat), srid=4326)
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        record = SensorData(
            sensor_id=sensor_id,
            location=point,
            pm25=pm25,
            temperature=temperature,
            timestamp=dt
        )
        db.add(record)
        inserted += 1

    db.commit()
    db.close()
    print(f"{inserted} Messungen gespeichert.")

if __name__ == "__main__":
    fetch_and_store()