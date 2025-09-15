from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class SensorDataBase(BaseModel):
    city: str
    aqi: int
    pm25: Optional[float]
    pm10: Optional[float]
    no2: Optional[float] = None
    o3: Optional[float] = None
    co: Optional[float] = None
    so2: Optional[float] = None
    lat: float
    lon: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class StationDataBase(BaseModel):
    station_uid: int
    station_name: str
    station_url: Optional[str] = None
    
    # Luftqualität
    aqi: Optional[int] = None
    
    # Schadstoffe
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    o3: Optional[float] = None
    co: Optional[float] = None
    so2: Optional[float] = None
    
    # Wetterdaten
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    
    # Koordinaten
    latitude: float
    longitude: float
    
    # Zeitstempel
    station_timestamp: Optional[str] = None
    
    # Metadaten
    source: str = "waqi_api"
    data_attribution: Optional[List[Dict[str, Any]]] = None
    region: str = "Berlin"

    model_config = ConfigDict(from_attributes=True)


class StationData(StationDataBase):
    id: int
    last_update: datetime

    model_config = ConfigDict(from_attributes=True)