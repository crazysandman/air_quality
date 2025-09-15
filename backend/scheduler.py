# backend/scheduler.py

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from database import get_db_session
from data_sources import get_data_source_manager
from crud import bulk_insert_station_data, cleanup_old_station_data, upsert_station_data
from models import StationData
from schemas import StationDataBase

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AirQualityScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def update_berlin_stations(self):
        """Aktualisiert alle Berlin Stationen und speichert sie in der Datenbank"""
        try:
            logger.info("Starte stündliche Aktualisierung der Berlin Stationen...")
            
            # Hole aktuelle Stationsdaten von allen aktiven Datenquellen
            import asyncio
            loop = asyncio.get_event_loop()
            
            # Use data source manager to get WAQI data
            data_manager = get_data_source_manager()
            waqi_features = await loop.run_in_executor(
                None, 
                lambda: data_manager.sources['waqi'].get_station_data('berlin')
            )
            
            if not waqi_features:
                logger.warning("Keine Stationsdaten von WAQI API erhalten")
                return
            
            # Konvertiere zu Pydantic Schema
            station_records = []
            features = waqi_features  # Direct list of features from data source
            for station in features:
                try:
                    # Extrahiere Daten aus dem GeoJSON Format
                    properties = station.get("properties", {})
                    coords = station.get("geometry", {}).get("coordinates", [0, 0])
                    
                    station_record = StationDataBase(
                        station_uid=properties.get("uid"),
                        station_name=properties.get("name", "Unknown"),
                        station_url=properties.get("url"),
                        aqi=properties.get("aqi"),
                        
                        # Schadstoffe
                        pm25=properties.get("pm25"),
                        pm10=properties.get("pm10"), 
                        no2=properties.get("no2"),
                        o3=properties.get("o3"),
                        co=properties.get("co"),
                        so2=properties.get("so2"),
                        
                        # Wetterdaten
                        temperature=properties.get("temperature"),
                        pressure=properties.get("pressure"),
                        humidity=properties.get("humidity"),
                        wind_speed=properties.get("wind_speed"),
                        
                        # Koordinaten
                        latitude=coords[1] if len(coords) > 1 else 0,
                        longitude=coords[0] if len(coords) > 0 else 0,
                        
                        # Zeitstempel
                        station_timestamp=properties.get("time"),
                        
                        # Metadaten
                        source="waqi_api",
                        data_attribution=properties.get("attributions"),
                        region="Berlin"
                    )
                    station_records.append(station_record)
                    
                except Exception as e:
                    logger.error(f"Fehler beim Verarbeiten von Station {properties.get('uid', 'unknown')}: {e}")
                    continue
            
            if not station_records:
                logger.warning("Keine gültigen Stationsdaten für Datenbank konvertiert")
                return
            
            # UPSERT in Datenbank (Update existing, Insert new)
            db = get_db_session()
            try:
                saved_records = upsert_station_data(db, station_records)
                logger.info(f"Erfolgreich {len(saved_records)} Stationen aktualisiert/eingefügt")
                
                # Note: Cleanup nicht mehr nötig da wir nur 16 Records haben
                # deleted_count = cleanup_old_station_data(db, days_to_keep=7)
                # if deleted_count > 0:
                #     logger.info(f"{deleted_count} alte Datensätze gelöscht")
                    
            except Exception as e:
                logger.error(f"Datenbankfehler: {e}")
                db.rollback()
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Fehler bei stündlicher Aktualisierung: {e}")
    
    def start_scheduler(self):
        """Startet den Scheduler für stündliche Updates"""
        if self.is_running:
            logger.info("Scheduler läuft bereits")
            return
        
        # Job für stündliche Aktualisierung hinzufügen
        # Läuft jede Stunde zur vollen Stunde
        self.scheduler.add_job(
            self.update_berlin_stations,
            trigger=CronTrigger(minute=0),  # Jede Stunde zur vollen Stunde
            id="berlin_stations_update",
            name="Berlin Stations Hourly Update",
            replace_existing=True
        )
        
        # Optional: Job für tägliche Cleanup-Aufgabe
        self.scheduler.add_job(
            self.cleanup_task,
            trigger=CronTrigger(hour=2, minute=0),  # Täglich um 2:00 Uhr
            id="database_cleanup",
            name="Database Cleanup",
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("Air Quality Scheduler gestartet - stündliche Updates aktiviert")
    
    async def cleanup_task(self):
        """Tägliche Aufräumarbeiten in der Datenbank"""
        try:
            logger.info("Starte tägliche Datenbankbereinigung...")
            db = get_db_session()
            try:
                deleted_count = cleanup_old_station_data(db, days_to_keep=7)
                logger.info(f"Tägliche Bereinigung: {deleted_count} alte Datensätze entfernt")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Fehler bei täglicher Bereinigung: {e}")
    
    def stop_scheduler(self):
        """Stoppt den Scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Air Quality Scheduler gestoppt")
    
    def get_status(self):
        """Gibt den Status des Schedulers zurück"""
        return {
            "running": self.is_running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ] if self.is_running else []
        }

# Global scheduler instance
scheduler_instance = AirQualityScheduler()
