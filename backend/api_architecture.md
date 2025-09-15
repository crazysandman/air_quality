# backend/api_architecture.md

# Air Quality API Architecture

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

### Implementation Steps:
1. ✅ Clean up old files and unused code
2. ✅ Keep current WAQI system working
3. 🔄 Add data source abstraction layer
4. 🔄 Update scheduler for multiple sources
5. 🔄 Add new API endpoints for source filtering
6. 🔄 Remove legacy sensor_data table
