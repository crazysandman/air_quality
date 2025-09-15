import requests
import schemas, crud
from sqlalchemy.orm import Session
from datetime import datetime
import os

WAQI_TOKEN = os.getenv("WAQI_API_TOKEN")

def fetch_waqi_data(city: str):
    url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Fehler beim Abrufen von WAQI-Daten: {response.status_code}")

    data = response.json()
    if data["status"] != "ok":
        raise Exception(f"WAQI API Error: {data.get('data', 'Unknown error')}")

    return data["data"]

def parse_and_store_waqi_data(db: Session, city: str):
    raw = fetch_waqi_data(city)

    try:
        parsed = schemas.SensorDataBase(
            city=city,
            aqi=raw["aqi"],
            pm25=raw["iaqi"].get("pm25", {}).get("v"),
            pm10=raw["iaqi"].get("pm10", {}).get("v"),
            no2=raw["iaqi"].get("no2", {}).get("v"),
            o3=raw["iaqi"].get("o3", {}).get("v"),
            co=raw["iaqi"].get("co", {}).get("v"),
            so2=raw["iaqi"].get("so2", {}).get("v"),
            lat=float(raw["city"]["geo"][0]),
            lon=float(raw["city"]["geo"][1]),
            timestamp=datetime.strptime(raw["time"]["s"], "%Y-%m-%d %H:%M:%S")
        )
        return crud.insert_sensor_data(db, parsed)

    except Exception as e:
        raise Exception(f"Fehler beim Parsen/Speichern der WAQI-Daten: {e}")