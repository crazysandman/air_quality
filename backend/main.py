from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi.responses import JSONResponse
from datetime import datetime
from db import SessionLocal, engine
from models import SensorData
from geoalchemy2.shape import to_shape

app = FastAPI()


# 📦 Datenbank-Tabelle (einmalig anlegen, falls nicht vorhanden)
SensorData.__table__.create(bind=engine, checkfirst=True)


# 🧩 Datenbank-Session bereitstellen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 Startpunkt
@app.get("/")
def root():
    return {"message": "Air Quality API läuft"}


# 🔸 GET /sensors – alle Daten mit Filteroptionen
@app.get("/sensors")
def get_all_sensors(
    after: str = Query(None),
    sensor_id: int = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(SensorData)

    if after:
        try:
            after_dt = datetime.fromisoformat(after)
            query = query.filter(SensorData.timestamp >= after_dt)
        except ValueError:
            return {"error": "Ungültiges Datumsformat. Verwende YYYY-MM-DD"}

    if sensor_id:
        query = query.filter(SensorData.sensor_id == sensor_id)

    results = query.order_by(SensorData.timestamp.desc()).all()
    return [
        {
            "id": r.id,
            "sensor_id": r.sensor_id,
            "timestamp": r.timestamp,
            "pm25": r.pm25,
            "temperature": r.temperature,
            "lat": to_shape(r.location).y,
            "lon": to_shape(r.location).x,
        }
        for r in results if r.location is not None
    ]


# 🌍 GET /sensors/geojson – GeoJSON-Ausgabe aller Messungen
@app.get("/sensors/geojson")
def get_sensors_geojson(after: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(SensorData)

    if after:
        try:
            after_dt = datetime.fromisoformat(after)
            query = query.filter(SensorData.timestamp >= after_dt)
        except ValueError:
            return {"error": "Ungültiges Datumsformat. Verwende YYYY-MM-DD"}

    features = []
    for r in query.all():
        if not r.location:
            continue

        geom = to_shape(r.location)
        lon = geom.x
        lat = geom.y

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "id": r.id,
                "sensor_id": r.sensor_id,
                "timestamp": r.timestamp.isoformat(),
                "pm25": r.pm25,
                "temperature": r.temperature
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return JSONResponse(content=geojson)