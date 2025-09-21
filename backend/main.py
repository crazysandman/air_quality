"""
Air Quality API Backend
======================

Main FastAPI application for the Air Quality monitoring system.
This module provides REST API endpoints for retrieving air quality data
from various monitoring stations in Berlin.

Author: Master's Student Project
Architecture: FastAPI + SQLAlchemy + PostgreSQL (Supabase)
External APIs: World Air Quality Index (WAQI) API
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

# Use relative imports for package structure (Railway deployment)
try:
    # When run as module (uvicorn backend.main:app)
    from . import database, schemas, crud, waqi_stations
    from .models import Base
    from .scheduler import scheduler_instance
except ImportError:
    # Fallback for direct execution (development)
    import database
    import schemas  
    import crud
    import waqi_stations
    from models import Base
    from scheduler import scheduler_instance
import asyncio
import os
from datetime import datetime

# FastAPI Application Instance
app = FastAPI(
    title="Air Quality API",
    description="REST API for Berlin Air Quality monitoring stations",
    version="1.0.0"
)

# CORS Configuration - Allow cross-origin requests from Android app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: Replace with specific Android app domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    
    Initializes database connection, creates tables if they don't exist,
    and starts the background scheduler for automatic data updates.
    """
    try:
        # Initialize database connection (PostgreSQL via Supabase or SQLite fallback)
        engine = database.initialize_database()
        
        # Create database tables using SQLAlchemy ORM models
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Start background scheduler for hourly WAQI API data updates
        scheduler_instance.start_scheduler()
        print("✅ Background scheduler started - hourly station updates enabled")
        
        # Service is ready for requests
        print("🚀 Air Quality API service ready")
        
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("API will still work for endpoints that don't require database")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    
    Gracefully stops the background scheduler and cleans up resources
    when the application is shutting down.
    """
    try:
        scheduler_instance.stop_scheduler()
        print("✅ Background scheduler stopped gracefully")
        
    except Exception as e:
        print(f"⚠️ Warning: Error stopping services: {e}")

# ========================================
# API ENDPOINTS
# ========================================

@app.get("/")
def root():
    """
    Root endpoint providing basic API information.
    
    Returns:
        dict: API status and version information
    """
    return {
        "message": "Air Quality API - Berlin Monitoring System", 
        "status": "healthy", 
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and keep-alive services.
    
    Verifies database connectivity and service status.
    Used by monitoring tools and deployment platforms.
    
    Returns:
        dict: Health status including database connectivity
    """
    try:
        # Test database connection
        db = database.get_db_session()
        result = db.execute("SELECT 1").fetchone()
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
    """
    Retrieve latest air quality data from all monitoring stations.
    
    This endpoint returns the most recent air quality measurements
    from all stations stored in the database.
    
    Args:
        limit (int, optional): Maximum number of stations to return
        db (Session): Database session dependency
        
    Returns:
        dict: Contains list of stations and total count
        
    Raises:
        HTTPException: 500 if database query fails
    """
    try:
        stations = crud.get_latest_station_data(db, limit)
        return {"stations": stations, "count": len(stations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stations/berlin")
def get_berlin_stations_from_db(db: Session = Depends(database.get_db)):
    """
    Retrieve latest air quality data specifically for Berlin stations.
    
    This endpoint filters and returns only monitoring stations
    located within the Berlin metropolitan area.
    
    Args:
        db (Session): Database session dependency
        
    Returns:
        dict: Contains Berlin stations list and count
        
    Raises:
        HTTPException: 500 if database query fails
    """
    try:
        stations = crud.get_latest_station_data_by_region(db, "Berlin")
        return {"stations": stations, "count": len(stations), "region": "Berlin"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stations/berlin/fresh")
async def get_fresh_berlin_stations(db: Session = Depends(database.get_db)):
    """Get fresh Berlin station data - updates database first, then returns latest data"""
    try:
        # First trigger an update to ensure we have the latest data
        await scheduler_instance.update_berlin_stations()
        
        # Then return the fresh data from database
        stations = crud.get_latest_station_data_by_region(db, "Berlin")
        return {"stations": stations, "count": len(stations), "region": "Berlin", "fresh": True}
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
