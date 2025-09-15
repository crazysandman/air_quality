# backend/api_architecture.md

# Air Quality API Archite### Current Production Status 🚀
- **Railway Deployment**: ✅ Live at `air-quality-production-a67b.up.railway.app`
- **Supabase Database**: ✅ 16 unique Berlin stations, UPSERT working perfectly
- **Data Source Manager**: ✅ WAQI active, OpenAQ/UBA ready for activation
- **Hourly Updates**: ✅ Scheduler running, no duplicate records
- **Next APIs**: Ready to activate with `data_manager.activate_source('openaq')`

### Available API Endpoints 🌐
```
GET /health                    - Health check
GET /stations/latest          - Latest data from all stations
GET /stations/region/berlin   - Berlin-specific station data
GET /scheduler/status         - Scheduler status and next run times
POST /scheduler/run           - Manual trigger for data collection
```

### Quick API Test:
```bash
# Check current station data
curl https://air-quality-production-a67b.up.railway.app/stations/latest

# Verify scheduler status  
curl https://air-quality-production-a67b.up.railway.app/scheduler/status
```
## Database Design for Multiple Data Sources

### Current Status ✅
- `station_data`: 16 WAQI Berlin stations (working perfectly)
- `sensor_data`: Empty, legacy table (to be removed)
- `spatial_ref_sys`: PostGIS system table (keep)

### Future Architecture 🚀

#### Single Unified Table: `station_data`
```sql
station_data:
- id (primary key)
- station_uid (unique per source)
- station_name
- source ("waqi_api", "openaq_api", "uba_api", etc.)
- region ("berlin", "munich", "hamburg", etc.)
- aqi, pm25, pm10, no2, o3, co, so2
- temperature, humidity, pressure, wind_speed
- latitude, longitude
- last_update
- data_attribution (JSON)
```

#### Benefits:
1. **Unified Data**: All sources in one table
2. **Source Tracking**: `source` field identifies data origin
3. **Regional Expansion**: Easy to add new cities
4. **API Compatibility**: Same endpoints work for all sources

#### Data Flow:
1. **Scheduler**: Collects from multiple sources
2. **UPSERT**: Updates by (station_uid + source) combination
3. **API**: Returns unified data regardless of source

### Example Data:
```
station_uid | source    | region | station_name           | aqi | pm25
10032      | waqi_api  | berlin | Neukölln-Nansenstraße  | 21  | 21.0
UBA123     | uba_api   | berlin | Berlin-Mitte           | 18  | 15.0
OAQ456     | openaq_api| munich | München-Zentrum        | 25  | 22.0
```

### Implementation Status:
1. ✅ Clean up old files and unused code
2. ✅ Keep current WAQI system working  
3. ✅ **COMPLETED**: Data source abstraction layer (`data_sources.py`)
4. ✅ **COMPLETED**: Scheduler updated for unified data source manager
5. ✅ **COMPLETED**: UPSERT system maintaining exactly 16 stations
6. 🔄 **TODO**: Remove legacy sensor_data table and endpoints
7. 🔄 **TODO**: Add new API endpoints for source filtering

### Current Production Status �
- **Railway Deployment**: ✅ Live at `air-quality-production-a67b.up.railway.app`
- **Supabase Database**: ✅ 16 unique Berlin stations, UPSERT working perfectly
- **Data Source Manager**: ✅ WAQI active, OpenAQ/UBA ready for activation
- **Hourly Updates**: ✅ Scheduler running, no duplicate records
- **Next APIs**: Ready to activate with `data_manager.activate_source('openaq')`
