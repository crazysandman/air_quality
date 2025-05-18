from sqlalchemy import Column, Integer, Float, DateTime
from geoalchemy2 import Geography
from db import Base
from datetime import datetime, timezone

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, index=True, nullable=False)
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    pm25 = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))