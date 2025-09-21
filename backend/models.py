"""
Database Models
===============

SQLAlchemy ORM models for the Air Quality monitoring system.
Defines the database schema for storing air quality station data.

Author: Master's Student Project
Database: PostgreSQL (Supabase) with SQLite fallback
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
import datetime

# Use relative imports for package structure
try:
    # When run as module (uvicorn backend.main:app)
    from .database import Base
except ImportError:
    # Fallback for direct execution (development)
    from database import Base

class SensorData(Base):
    """
    Legacy sensor data model - kept for backward compatibility.
    
    Simplified model for basic air quality measurements.
    Consider migrating to StationData model for new implementations.
    """
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
    """
    Main air quality station data model.
    
    Comprehensive model storing all air quality measurements from WAQI API.
    Includes pollutant concentrations, weather data, and station metadata.
    
    Attributes:
        id: Primary key
        station_uid: Unique identifier from WAQI API
        station_name: Human-readable station name
        station_url: Direct link to station on WAQI website
        aqi: Air Quality Index (main indicator)
        pm25, pm10, no2, o3, co, so2: Pollutant concentrations
        temperature, pressure, humidity, wind_speed: Weather data
        latitude, longitude: Geographic coordinates
        station_timestamp: Original timestamp from API
        last_update: When record was stored in our database
        source: Data source identifier
        data_attribution: Attribution metadata from EPA/WAQI
        region: Geographic region (default: Berlin)
    """
    __tablename__ = "station_data"

    id = Column(Integer, primary_key=True, index=True)
    station_uid = Column(Integer, index=True, nullable=False)
    station_name = Column(String, index=True)
    station_url = Column(String, nullable=True)
    
    # Air Quality Measurements
    aqi = Column(Integer, nullable=True)  # Main Air Quality Index
    
    # Pollutant Concentrations (Individual Air Quality Index values)
    pm25 = Column(Float, nullable=True)      # Fine particulate matter (μg/m³)
    pm10 = Column(Float, nullable=True)      # Coarse particulate matter (μg/m³)
    no2 = Column(Float, nullable=True)       # Nitrogen dioxide (μg/m³)
    o3 = Column(Float, nullable=True)        # Ozone (μg/m³)
    co = Column(Float, nullable=True)        # Carbon monoxide (mg/m³)
    so2 = Column(Float, nullable=True)       # Sulfur dioxide (μg/m³)
    
    # Weather Data (when available from station)
    temperature = Column(Float, nullable=True)   # Temperature (°C)
    pressure = Column(Float, nullable=True)      # Atmospheric pressure (hPa)
    humidity = Column(Float, nullable=True)      # Relative humidity (%)
    wind_speed = Column(Float, nullable=True)    # Wind speed (m/s)
    
    # Geographic Location
    latitude = Column(Float, nullable=False)     # Latitude coordinate
    longitude = Column(Float, nullable=False)    # Longitude coordinate
    
    # Temporal Data
    station_timestamp = Column(String, nullable=True)    # Original API timestamp
    last_update = Column(DateTime, default=datetime.datetime.utcnow)  # Database insert time
    
    # Metadata
    source = Column(String, default="waqi_api")          # Data source identifier
    data_attribution = Column(JSON, nullable=True)       # EPA attribution data
    region = Column(String, default="Berlin", index=True)  # Geographic region filter