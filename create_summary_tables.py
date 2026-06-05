import sqlite3
import time

db_name = "airline_performance.db"

print("Connecting to database...")
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Enable WAL mode for performance
cursor.execute("PRAGMA journal_mode=WAL")
cursor.execute("PRAGMA synchronous=NORMAL")

print("Creating pre-aggregated summary tables...")

# 1. Create agg_airline_monthly
print("1/6 Creating agg_airline_monthly...")
t0 = time.time()
cursor.execute("DROP TABLE IF EXISTS agg_airline_monthly")
cursor.execute("""
    CREATE TABLE agg_airline_monthly AS
    SELECT
        f.MONTH,
        f.AIRLINE AS AIRLINE_CODE,
        al.AIRLINE AS AIRLINE_NAME,
        COUNT(*) AS total_flights,
        SUM(f.CANCELLED) AS cancelled_flights,
        SUM(f.DIVERTED) AS diverted_flights,
        SUM(coalesce(f.DEPARTURE_DELAY, 0)) AS total_dep_delay,
        SUM(coalesce(f.ARRIVAL_DELAY, 0)) AS total_arr_delay,
        SUM(CASE WHEN f.ARRIVAL_DELAY <= 15 AND f.CANCELLED = 0 AND f.DIVERTED = 0 THEN 1 ELSE 0 END) AS on_time_arrivals,
        SUM(CASE WHEN f.DEPARTURE_DELAY <= 15 AND f.CANCELLED = 0 AND f.DIVERTED = 0 THEN 1 ELSE 0 END) AS on_time_departures
    FROM flights_raw f
    LEFT JOIN airlines al ON f.AIRLINE = al.IATA_CODE
    GROUP BY f.MONTH, f.AIRLINE, al.AIRLINE
""")
conn.commit()
print(f"Created agg_airline_monthly in {time.time() - t0:.2f} seconds.")

# 2. Create agg_airport_monthly
print("2/6 Creating agg_airport_monthly...")
t0 = time.time()
cursor.execute("DROP TABLE IF EXISTS agg_airport_monthly")
cursor.execute("""
    CREATE TABLE agg_airport_monthly AS
    SELECT
        f.MONTH,
        f.AIRLINE AS AIRLINE_CODE,
        coalesce(map_org.IATA_CODE, f.ORIGIN_AIRPORT) AS AIRPORT_CODE,
        COUNT(*) AS total_flights,
        SUM(f.CANCELLED) AS cancelled_flights,
        SUM(f.DIVERTED) AS diverted_flights,
        SUM(coalesce(f.DEPARTURE_DELAY, 0)) AS total_dep_delay,
        SUM(coalesce(f.ARRIVAL_DELAY, 0)) AS total_arr_delay,
        SUM(CASE WHEN f.ARRIVAL_DELAY <= 15 AND f.CANCELLED = 0 AND f.DIVERTED = 0 THEN 1 ELSE 0 END) AS on_time_arrivals
    FROM flights_raw f
    LEFT JOIN airport_mappings map_org ON f.ORIGIN_AIRPORT = map_org.AIRPORT_ID
    GROUP BY f.MONTH, f.AIRLINE, AIRPORT_CODE
""")
conn.commit()
print(f"Created agg_airport_monthly in {time.time() - t0:.2f} seconds.")

# 3. Create agg_temporal_daily
print("3/6 Creating agg_temporal_daily...")
t0 = time.time()
cursor.execute("DROP TABLE IF EXISTS agg_temporal_daily")
cursor.execute("""
    CREATE TABLE agg_temporal_daily AS
    SELECT
        f.MONTH,
        f.AIRLINE AS AIRLINE_CODE,
        f.DAY_OF_WEEK,
        COUNT(*) AS total_flights,
        SUM(f.CANCELLED) AS cancelled_flights,
        SUM(coalesce(f.DEPARTURE_DELAY, 0)) AS total_dep_delay,
        SUM(CASE WHEN f.ARRIVAL_DELAY <= 15 AND f.CANCELLED = 0 AND f.DIVERTED = 0 THEN 1 ELSE 0 END) AS on_time_arrivals
    FROM flights_raw f
    GROUP BY f.MONTH, f.AIRLINE, f.DAY_OF_WEEK
""")
conn.commit()
print(f"Created agg_temporal_daily in {time.time() - t0:.2f} seconds.")

# 4. Create agg_temporal_hourly
print("4/6 Creating agg_temporal_hourly...")
t0 = time.time()
cursor.execute("DROP TABLE IF EXISTS agg_temporal_hourly")
cursor.execute("""
    CREATE TABLE agg_temporal_hourly AS
    SELECT
        f.MONTH,
        f.AIRLINE AS AIRLINE_CODE,
        CAST(substr(printf('%04d', cast(f.SCHEDULED_DEPARTURE as int)), 1, 2) AS INT) AS HOUR,
        COUNT(*) AS total_flights,
        SUM(coalesce(f.DEPARTURE_DELAY, 0)) AS total_dep_delay,
        SUM(CASE WHEN f.ARRIVAL_DELAY <= 15 AND f.CANCELLED = 0 AND f.DIVERTED = 0 THEN 1 ELSE 0 END) AS on_time_arrivals
    FROM flights_raw f
    GROUP BY f.MONTH, f.AIRLINE, HOUR;
""")
conn.commit()
print(f"Created agg_temporal_hourly in {time.time() - t0:.2f} seconds.")

# 5. Create agg_cancellations_monthly
print("5/6 Creating agg_cancellations_monthly...")
t0 = time.time()
cursor.execute("DROP TABLE IF EXISTS agg_cancellations_monthly")
cursor.execute("""
    CREATE TABLE agg_cancellations_monthly AS
    SELECT
        f.MONTH,
        f.AIRLINE AS AIRLINE_CODE,
        CASE f.CANCELLATION_REASON
            WHEN 'A' THEN 'Carrier'
            WHEN 'B' THEN 'Weather'
            WHEN 'C' THEN 'National Air System (NAS)'
            WHEN 'D' THEN 'Security'
            ELSE 'Unknown'
        END AS Reason,
        COUNT(*) AS Count
    FROM flights_raw f
    WHERE f.CANCELLED = 1
    GROUP BY f.MONTH, f.AIRLINE, Reason
""")
conn.commit()
print(f"Created agg_cancellations_monthly in {time.time() - t0:.2f} seconds.")

# 6. Create agg_delay_types_monthly
print("6/6 Creating agg_delay_types_monthly...")
t0 = time.time()
cursor.execute("DROP TABLE IF EXISTS agg_delay_types_monthly")
cursor.execute("""
    CREATE TABLE agg_delay_types_monthly AS
    SELECT
        f.MONTH,
        f.AIRLINE AS AIRLINE_CODE,
        SUM(f.AIRLINE_DELAY) AS Airline,
        SUM(f.WEATHER_DELAY) AS Weather,
        SUM(f.AIR_SYSTEM_DELAY) AS [National Air System (NAS)],
        SUM(f.SECURITY_DELAY) AS Security,
        SUM(f.LATE_AIRCRAFT_DELAY) AS [Late Aircraft]
    FROM flights_raw f
    GROUP BY f.MONTH, f.AIRLINE
""")
conn.commit()
print(f"Created agg_delay_types_monthly in {time.time() - t0:.2f} seconds.")

# Add indexes to pre-aggregated tables for instantaneous lookups
print("Creating indexes on pre-aggregated tables...")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_agg_air_mo ON agg_airline_monthly (MONTH, AIRLINE_CODE)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_agg_apt_mo ON agg_airport_monthly (MONTH, AIRLINE_CODE, AIRPORT_CODE)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_agg_day_mo ON agg_temporal_daily (MONTH, AIRLINE_CODE, DAY_OF_WEEK)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_agg_hr_mo ON agg_temporal_hourly (MONTH, AIRLINE_CODE, HOUR)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_agg_can_mo ON agg_cancellations_monthly (MONTH, AIRLINE_CODE, Reason)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_agg_dly_mo ON agg_delay_types_monthly (MONTH, AIRLINE_CODE)")
conn.commit()

conn.close()
print("All pre-aggregated summary tables successfully created!")
