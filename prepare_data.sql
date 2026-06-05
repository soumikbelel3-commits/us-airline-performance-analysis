-- SQL script for data preparation, cleaning, and integration

-- 1. Create clean airlines table
DROP TABLE IF EXISTS airlines;
CREATE TABLE airlines (
    IATA_CODE TEXT PRIMARY KEY,
    AIRLINE TEXT
);
INSERT INTO airlines (IATA_CODE, AIRLINE)
SELECT IATA_CODE, AIRLINE FROM airlines_raw;

-- 2. Create clean airports table
DROP TABLE IF EXISTS airports;
CREATE TABLE airports (
    IATA_CODE TEXT PRIMARY KEY,
    AIRPORT TEXT,
    CITY TEXT,
    STATE TEXT,
    COUNTRY TEXT,
    LATITUDE REAL,
    LONGITUDE REAL
);
INSERT INTO airports (IATA_CODE, AIRPORT, CITY, STATE, COUNTRY, LATITUDE, LONGITUDE)
SELECT IATA_CODE, AIRPORT, CITY, STATE, COUNTRY, CAST(LATITUDE AS REAL), CAST(LONGITUDE AS REAL) FROM airports_raw;

-- 3. Create indexes on flights_raw to optimize performance
CREATE INDEX IF NOT EXISTS idx_flights_airline ON flights_raw (AIRLINE);
CREATE INDEX IF NOT EXISTS idx_flights_origin ON flights_raw (ORIGIN_AIRPORT);
CREATE INDEX IF NOT EXISTS idx_flights_dest ON flights_raw (DESTINATION_AIRPORT);
CREATE INDEX IF NOT EXISTS idx_flights_month ON flights_raw (MONTH);
CREATE INDEX IF NOT EXISTS idx_flights_dayofweek ON flights_raw (DAY_OF_WEEK);

-- 4. Create unified analytical view
DROP VIEW IF EXISTS v_flights_analytical;
CREATE VIEW v_flights_analytical AS
SELECT
    f.YEAR,
    f.MONTH,
    f.DAY,
    f.DAY_OF_WEEK,
    f.AIRLINE AS AIRLINE_CODE,
    al.AIRLINE AS AIRLINE_NAME,
    f.FLIGHT_NUMBER,
    f.TAIL_NUMBER,
    coalesce(map_org.IATA_CODE, f.ORIGIN_AIRPORT) AS ORIGIN_AIRPORT,
    ap_org.AIRPORT AS ORIGIN_AIRPORT_NAME,
    ap_org.CITY AS ORIGIN_CITY,
    ap_org.STATE AS ORIGIN_STATE,
    ap_org.LATITUDE AS ORIGIN_LATITUDE,
    ap_org.LONGITUDE AS ORIGIN_LONGITUDE,
    coalesce(map_dest.IATA_CODE, f.DESTINATION_AIRPORT) AS DESTINATION_AIRPORT,
    ap_dest.AIRPORT AS DEST_AIRPORT_NAME,
    ap_dest.CITY AS DEST_CITY,
    ap_dest.STATE AS DEST_STATE,
    ap_dest.LATITUDE AS DEST_LATITUDE,
    ap_dest.LONGITUDE AS DEST_LONGITUDE,
    f.SCHEDULED_DEPARTURE,
    f.DEPARTURE_TIME,
    coalesce(f.DEPARTURE_DELAY, 0) AS DEPARTURE_DELAY,
    f.TAXI_OUT,
    f.WHEELS_OFF,
    f.SCHEDULED_TIME,
    f.ELAPSED_TIME,
    f.AIR_TIME,
    f.DISTANCE,
    f.WHEELS_ON,
    f.TAXI_IN,
    f.SCHEDULED_ARRIVAL,
    f.ARRIVAL_TIME,
    coalesce(f.ARRIVAL_DELAY, 0) AS ARRIVAL_DELAY,
    f.DIVERTED,
    f.CANCELLED,
    f.CANCELLATION_REASON,
    CASE f.CANCELLATION_REASON
        WHEN 'A' THEN 'Carrier'
        WHEN 'B' THEN 'Weather'
        WHEN 'C' THEN 'National Air System (NAS)'
        WHEN 'D' THEN 'Security'
        ELSE NULL
    END AS CANCELLATION_REASON_DESC,
    coalesce(f.AIR_SYSTEM_DELAY, 0) AS AIR_SYSTEM_DELAY,
    coalesce(f.SECURITY_DELAY, 0) AS SECURITY_DELAY,
    coalesce(f.AIRLINE_DELAY, 0) AS AIRLINE_DELAY,
    coalesce(f.LATE_AIRCRAFT_DELAY, 0) AS LATE_AIRCRAFT_DELAY,
    coalesce(f.WEATHER_DELAY, 0) AS WEATHER_DELAY,
    
    -- Date formatting
    printf('%04d-%02d-%02d', f.YEAR, f.MONTH, f.DAY) AS FLIGHT_DATE,
    
    -- Scheduled departure datetime (HHMM padded and formatted)
    printf('%04d-%02d-%02d %s:%s:00', f.YEAR, f.MONTH, f.DAY, 
        substr(printf('%04d', cast(f.SCHEDULED_DEPARTURE as int)), 1, 2), 
        substr(printf('%04d', cast(f.SCHEDULED_DEPARTURE as int)), 3, 2)) AS SCHEDULED_DEPARTURE_DATETIME,
        
    -- Scheduled arrival datetime (HHMM padded and formatted)
    printf('%04d-%02d-%02d %s:%s:00', f.YEAR, f.MONTH, f.DAY, 
        substr(printf('%04d', cast(f.SCHEDULED_ARRIVAL as int)), 1, 2), 
        substr(printf('%04d', cast(f.SCHEDULED_ARRIVAL as int)), 3, 2)) AS SCHEDULED_ARRIVAL_DATETIME
FROM flights_raw f
LEFT JOIN airport_mappings map_org ON f.ORIGIN_AIRPORT = map_org.AIRPORT_ID
LEFT JOIN airport_mappings map_dest ON f.DESTINATION_AIRPORT = map_dest.AIRPORT_ID
LEFT JOIN airlines al ON f.AIRLINE = al.IATA_CODE
LEFT JOIN airports ap_org ON coalesce(map_org.IATA_CODE, f.ORIGIN_AIRPORT) = ap_org.IATA_CODE
LEFT JOIN airports ap_dest ON coalesce(map_dest.IATA_CODE, f.DESTINATION_AIRPORT) = ap_dest.IATA_CODE;
