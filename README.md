# Air Quality Monitoring System
## Master's Student Project

### Overview
A comprehensive air quality monitoring system consisting of a FastAPI backend and Android mobile application. The system provides real-time air quality data visualization with interactive maps and location-based features.

### Architecture

```
air_quality/
├── backend/                 # FastAPI REST API Server
│   ├── main.py             # Main application entry point
│   ├── models.py           # SQLAlchemy ORM models
│   ├── database.py         # Database configuration
│   ├── crud.py             # Database operations
│   ├── schemas.py          # Pydantic schemas
│   ├── waqi_service.py     # World Air Quality Index API integration
│   ├── waqi_stations.py    # Station data management
│   ├── scheduler.py        # Background data updates
│   ├── config.py           # Configuration management
│   ├── keep_alive.py       # Service monitoring
│   └── data_sources.py     # External data source handling
│
└── air_quality_app_android/    # Android Mobile Application
    └── app/src/main/java/de/project/air_quality_app/
        ├── MainActivity.kt                # Main UI with Mapbox integration
        ├── viewmodel/
        │   └── AirQualityViewModel.kt    # MVVM state management
        ├── models/
        │   └── StationData.kt           # Data models
        ├── repository/
        │   └── AirQualityRepository.kt  # Data layer abstraction
        ├── network/
        │   └── ApiService.kt            # Network layer
        ├── location/
        │   └── LocationManager.kt       # GPS services
        └── utils/
            └── LocationUtils.kt         # Geographic calculations
```

### Tech Stack

#### Backend
- **FastAPI** - Modern, fast web framework for APIs
- **SQLAlchemy** - Python SQL toolkit and ORM
- **PostgreSQL** - Primary database (Supabase)
- **SQLite** - Development fallback database
- **APScheduler** - Background task scheduling
- **WAQI API** - World Air Quality Index data source

#### Android App
- **Kotlin** - Primary programming language
- **Jetpack Compose** - Modern UI toolkit
- **Mapbox SDK** - Interactive mapping
- **Google Location Services** - GPS functionality
- **Retrofit** - HTTP client for API communication
- **MVVM Architecture** - Clean separation of concerns

### Features

#### Backend API
- RESTful API with automatic documentation
- Real-time air quality data from 50+ Berlin stations
- Automated hourly data updates
- PostgreSQL database with fallback support
- Railway deployment ready
- Health monitoring endpoints

#### Android Application
- Interactive dark-themed map with custom markers
- GPS location tracking with permission handling
- Color-coded AQI (Air Quality Index) visualization
- Responsive Material Design 3 UI
- Detailed station information cards
- Custom navigation controls
- Real-time data updates

### API Endpoints

```
GET /                    # API status and version
GET /health             # Health check for monitoring
GET /stations/latest    # Latest data from all stations
GET /stations/berlin    # Berlin-specific station data
```

### Data Model

Each air quality station includes:
- **Location**: Latitude, longitude, station name
- **AQI**: Overall Air Quality Index (0-500+)
- **Pollutants**: PM2.5, PM10, NO₂, O₃, SO₂, CO
- **Weather**: Temperature, humidity, pressure, wind
- **Metadata**: Data source, timestamps, attribution

### Setup Instructions

#### Backend Deployment
1. Set environment variables for database connection
2. Install dependencies: `pip install -r requirements.txt`
3. Run with: `uvicorn main:app --host 0.0.0.0 --port 8000`

#### Android Development
1. Open project in Android Studio
2. Add Mapbox API key to local.properties
3. Build and run on device/emulator

### Data Sources
- **WAQI API**: World Air Quality Index Project
- **EPA**: Environmental Protection Agency standards
- **Supabase**: PostgreSQL database hosting

### License
Master's Student Project - Academic Use


Dieses Projekt kombiniert eine Android-App mit einer Python-basierten REST-API und einer räumlich erweiterten PostgreSQL/PostGIS-Datenbank, um offene IoT-Daten zur Luftqualität (z. B. von Sensor.Community) interaktiv auf einer Karte anzuzeigen.

# Datenquelle

Sensor.Community API


# Technologien:

Python (FastAPI, SQLAlchemy, GeoAlchemy)
PostgreSQL + PostGIS
Android SDK (Kotlin)
Mapbox SDK
Docker + Docker Compose
Git & GitHub für Versionskontrolle
