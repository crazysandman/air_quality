from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from database import Base
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    aqi = Column(Integer)
    pm25 = Column(Float)
    pm10 = Column(Float)
    no2 = Column(Float, nullable=True)
    o3 = Column(Float, nullable=True)
    co = Column(Float, nullable=True)
    so2 = Column(Float, nullable=True)
    lat = Column(Float)
    lon = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class StationData(Base):
    __tablename__ = "station_data"

    id = Column(Integer, primary_key=True, index=True)
    station_uid = Column(Integer, index=True, nullable=False)
    station_name = Column(String, index=True)
    station_url = Column(String, nullable=True)
    
    # Luftqualität
    aqi = Column(Integer, nullable=True)
    
    # Schadstoffe (Individual Air Quality Index Werte)
    pm25 = Column(Float, nullable=True)
    pm10 = Column(Float, nullable=True)
    no2 = Column(Float, nullable=True)
    o3 = Column(Float, nullable=True)
    co = Column(Float, nullable=True)
    so2 = Column(Float, nullable=True)
    
    # Wetterdaten
    temperature = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    
    # Koordinaten
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Zeitstempel
    station_timestamp = Column(String, nullable=True)  # Original API timestamp
    last_update = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Metadaten
    source = Column(String, default="waqi_api")
    data_attribution = Column(JSON, nullable=True)  # EPA attribution data
    region = Column(String, default="Berlin", index=True)