from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import database, schemas, crud
import waqi_stations
from models import Base
from scheduler import scheduler_instance
import asyncio
import os
from datetime import datetime

app = FastAPI()

# CORS-Konfiguration (für deine Android-App)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # oder spezifische Domain z. B. ["http://192.168.0.12:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    try:
        # Initialize database connection
        engine = database.initialize_database()
        
        # Create database tables (should work with SQLite fallback)
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
        # Start the scheduler for hourly updates
        scheduler_instance.start_scheduler()
        print("Air Quality Scheduler started for hourly station updates")
        
        # Note: Keep-alive temporarily disabled for deployment debugging
        print("System ready - Railway will manage service lifecycle")
        
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("API will still work for endpoints that don't require database")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        scheduler_instance.stop_scheduler()
        print("Air Quality Scheduler stopped")
        
    except Exception as e:
        print(f"Warning: Error stopping services: {e}")

# Use the database module's get_db function directly
# (removing duplicate definition)

# ----------------------------------------
# Root-Endpunkt
# ----------------------------------------
@app.get("/")
def root():
    return {"message": "WAQI Backend is running"}

# ----------------------------------------
# Health Check Endpoint (für Keep-Alive)
# ----------------------------------------
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring and keep-alive"""
    try:
        # Check database connection
        db = database.get_db_session()
        db.execute("SELECT 1")
        db_status = "connected"
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    
    # Check scheduler status
    scheduler_status = "running" if scheduler_instance.scheduler.running else "stopped"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "scheduler": scheduler_status,
        "environment": os.getenv("RAILWAY_ENVIRONMENT_NAME", "local")
    }

# ----------------------------------------
# Station Data Endpoints (New Unified API)
# ----------------------------------------
@app.get("/stations/latest")
def get_latest_stations(limit: int = None, db: Session = Depends(database.get_db)):
    """Get latest station data from database"""
    try:
        stations = crud.get_latest_station_data(db, limit)
        return {"stations": stations, "count": len(stations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stations/berlin")
def get_berlin_stations_from_db(db: Session = Depends(database.get_db)):
    """Get latest Berlin station data from database"""
    try:
        stations = crud.get_latest_station_data_by_region(db, "Berlin")
        return {"stations": stations, "count": len(stations), "region": "Berlin"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scheduler/run")
async def trigger_manual_update():
    """Manually trigger a station data update"""
    try:
        await scheduler_instance.update_berlin_stations()
        return {"status": "success", "message": "Manual update completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stations/region/{region}")
def get_stations_by_region(region: str, db: Session = Depends(database.get_db)):
    """Get latest station data for a specific region"""
    try:
        stations = crud.get_latest_station_data_by_region(db, region.title())
        return {"stations": stations, "count": len(stations), "region": region}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduler/status")
def get_scheduler_status():
    """Get status of the air quality scheduler"""
    try:
        return scheduler_instance.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
