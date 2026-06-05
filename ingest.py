import sqlite3
import pandas as pd
import os
import time

db_name = "airline_performance.db"
flights_csv = "flights.csv"
airlines_csv = "airlines.csv"
airports_csv = "airports.csv"

# Clear existing db to prevent duplication if re-run
if os.path.exists(db_name):
    print(f"Removing existing database: {db_name}")
    try:
        os.remove(db_name)
    except PermissionError:
        print(f"Could not remove {db_name}, it might be open. Attempting to overwrite tables instead.")

print("Connecting to SQLite database...")
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# 1. Ingest airlines
print("Ingesting airlines...")
airlines_df = pd.read_csv(airlines_csv)
airlines_df.to_sql("airlines_raw", conn, if_exists="replace", index=False)
print(f"Loaded {len(airlines_df)} rows into airlines_raw.")

# 2. Ingest airports
print("Ingesting airports...")
airports_df = pd.read_csv(airports_csv)
airports_df.to_sql("airports_raw", conn, if_exists="replace", index=False)
print(f"Loaded {len(airports_df)} rows into airports_raw.")

# 3. Ingest flights
print("Ingesting flights (this may take a moment as it's ~592MB)...")
start_time = time.time()
chunksize = 200000
total_rows = 0

# Clear existing table if we couldn't delete file
cursor.execute("DROP TABLE IF EXISTS flights_raw")
conn.commit()

# We will read flights.csv in chunks
for chunk in pd.read_csv(flights_csv, chunksize=chunksize, dtype={
    'YEAR': 'Int32', 'MONTH': 'Int32', 'DAY': 'Int32', 'DAY_OF_WEEK': 'Int32',
    'AIRLINE': str, 'FLIGHT_NUMBER': str, 'TAIL_NUMBER': str,
    'ORIGIN_AIRPORT': str, 'DESTINATION_AIRPORT': str,
    'SCHEDULED_DEPARTURE': str, 'DEPARTURE_TIME': str,
    'WHEELS_OFF': str, 'SCHEDULED_ARRIVAL': str, 'ARRIVAL_TIME': str,
    'WHEELS_ON': str, 'CANCELLATION_REASON': str
}):
    chunk.to_sql("flights_raw", conn, if_exists="append", index=False)
    total_rows += len(chunk)
    print(f"Loaded {total_rows} rows...", end="\r")

end_time = time.time()
print(f"\nSuccessfully loaded {total_rows} rows into flights_raw in {end_time - start_time:.2f} seconds.")

# Verify row counts
cursor.execute("SELECT COUNT(*) FROM airlines_raw")
print(f"Airlines raw count: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM airports_raw")
print(f"Airports raw count: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM flights_raw")
print(f"Flights raw count: {cursor.fetchone()[0]}")

# Perform a quick sample validation
cursor.execute("SELECT * FROM flights_raw LIMIT 2")
sample = cursor.fetchall()
print("Sample flights data loaded:")
for row in sample:
    print(row[:10]) # print first 10 columns

conn.close()
print("Ingestion completed!")
