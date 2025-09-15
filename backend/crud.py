# backend/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text, desc
from datetime import datetime, timedelta
import models
import schemas

# Neue Messung speichern
def insert_sensor_data(db: Session, data: schemas.SensorDataBase):
    db_item = models.SensorData(**data.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Alle Daten abrufen
def get_all_sensor_data(db: Session):
    return db.query(models.SensorData).all()

# Optional: Daten nach Stadtname filtern
def get_sensor_data_by_city(db: Session, city_name: str):
    return db.query(models.SensorData).filter(models.SensorData.city == city_name).all()


# Station data CRUD operations
def insert_station_data(db: Session, data: schemas.StationDataBase):
    db_item = models.StationData(**data.dict())
    db_item.last_update = datetime.utcnow()
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def bulk_insert_station_data(db: Session, station_data_list: list[schemas.StationDataBase]):
    """Batch insert für mehrere Stationen gleichzeitig"""
    db_items = []
    current_time = datetime.utcnow()
    
    for data in station_data_list:
        db_item = models.StationData(**data.dict())
        db_item.last_update = current_time
        db_items.append(db_item)
    
    db.add_all(db_items)
    db.commit()
    
    for item in db_items:
        db.refresh(item)
    
    return db_items

def upsert_station_data(db: Session, station_data_list: list[schemas.StationDataBase]):
    """
    UPSERT: Update existing stations or insert new ones
    Keeps only 16 current stations (one per station_uid)
    """
    current_time = datetime.utcnow()
    updated_stations = []
    
    for data in station_data_list:
        # Check if station already exists
        existing_station = db.query(models.StationData).filter(
            models.StationData.station_uid == data.station_uid
        ).first()
        
        if existing_station:
            # UPDATE existing record
            for field, value in data.dict().items():
                if field != 'station_uid':  # Don't update UID
                    setattr(existing_station, field, value)
            existing_station.last_update = current_time
            updated_stations.append(existing_station)
        else:
            # INSERT new record
            db_item = models.StationData(**data.dict())
            db_item.last_update = current_time
            db.add(db_item)
            updated_stations.append(db_item)
    
    db.commit()
    
    # Refresh all items
    for item in updated_stations:
        db.refresh(item)
    
    return updated_stations

def get_latest_station_data(db: Session, limit: int = None):
    """Holt die neuesten Daten für alle Stationen"""
    query = db.query(models.StationData).order_by(desc(models.StationData.last_update))
    if limit:
        query = query.limit(limit)
    return query.all()

def get_station_data_by_uid(db: Session, station_uid: int):
    """Holt alle Daten für eine bestimmte Station"""
    return db.query(models.StationData).filter(
        models.StationData.station_uid == station_uid
    ).order_by(desc(models.StationData.last_update)).all()

def get_latest_station_data_by_region(db: Session, region: str = "Berlin"):
    """Holt die neuesten Daten aller Stationen einer Region"""
    # Subquery für die neueste last_update Zeit pro station_uid
    latest_times = db.query(
        models.StationData.station_uid,
        func.max(models.StationData.last_update).label('max_time')
    ).filter(models.StationData.region == region).group_by(models.StationData.station_uid).subquery()
    
    # Join mit der Haupttabelle für die vollständigen Datensätze
    return db.query(models.StationData).join(
        latest_times,
        and_(
            models.StationData.station_uid == latest_times.c.station_uid,
            models.StationData.last_update == latest_times.c.max_time
        )
    ).all()

def cleanup_old_station_data(db: Session, days_to_keep: int = 7):
    """Löscht Stationsdaten älter als X Tage"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    deleted_count = db.query(models.StationData).filter(
        models.StationData.last_update < cutoff_date
    ).delete()
    db.commit()
    return deleted_count