-- =====================================
-- SUPABASE DATABASE SETUP FÜR AIR QUALITY APP
-- =====================================

-- 1. PostGIS Extension aktivieren (für Geodaten)
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Haupttabelle für Stationsdaten erstellen
CREATE TABLE IF NOT EXISTS station_data (
    id SERIAL PRIMARY KEY,
    station_uid INTEGER NOT NULL,
    station_name VARCHAR(255),
    station_url VARCHAR(500),
    
    -- Air Quality Index
    aqi INTEGER,
    
    -- Pollutants (Schadstoffe)
    pm25 DECIMAL(10,2),      -- PM2.5
    pm10 DECIMAL(10,2),      -- PM10
    no2 DECIMAL(10,2),       -- Stickstoffdioxid
    o3 DECIMAL(10,2),        -- Ozon
    co DECIMAL(10,2),        -- Kohlenmonoxid
    so2 DECIMAL(10,2),       -- Schwefeldioxid
    
    -- Weather data (Wetterdaten)
    temperature DECIMAL(5,2),
    humidity INTEGER,
    pressure DECIMAL(7,2),
    wind_speed DECIMAL(5,2),
    
    -- Location (mit PostGIS Point für räumliche Abfragen)
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    location GEOMETRY(POINT, 4326),  -- PostGIS Point
    
    -- Metadata
    region VARCHAR(100) DEFAULT 'Berlin',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Spatial Index für Location erstellen (für schnelle Geo-Abfragen)
CREATE INDEX IF NOT EXISTS idx_station_data_location 
ON station_data USING GIST (location);

-- 4. Weitere Indices für Performance
CREATE INDEX IF NOT EXISTS idx_station_data_timestamp 
ON station_data (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_station_data_station_uid 
ON station_data (station_uid);

CREATE INDEX IF NOT EXISTS idx_station_data_region 
ON station_data (region);

-- 5. Trigger: Automatisch location Point aus lat/lng erstellen
CREATE OR REPLACE FUNCTION update_location_point()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_location_point
    BEFORE INSERT OR UPDATE ON station_data
    FOR EACH ROW
    EXECUTE FUNCTION update_location_point();

-- 6. Legacy Tabelle für bestehende Daten (falls vorhanden)
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    aqi INTEGER,
    pm25 DECIMAL(5,2),
    pm10 DECIMAL(5,2),
    lat DECIMAL(10,6),
    lon DECIMAL(10,6),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. RLS (Row Level Security) Policy - Optional für Sicherheit
-- ALTER TABLE station_data ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow all access for now" ON station_data FOR ALL USING (true);

-- 8. Test-Query zum Verifizieren
SELECT 
    'PostGIS Extension' as check_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'postgis'
    ) THEN '✅ Installed' ELSE '❌ Missing' END as status
UNION ALL
SELECT 
    'station_data table' as check_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'station_data'
    ) THEN '✅ Created' ELSE '❌ Missing' END as status
UNION ALL
SELECT 
    'Spatial index' as check_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_station_data_location'
    ) THEN '✅ Created' ELSE '❌ Missing' END as status;

-- Ende des Setup-Scripts
