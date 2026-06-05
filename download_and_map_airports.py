import sqlite3
import urllib.request
import os
import re

db_name = "airline_performance.db"
lookup_url = "https://raw.githubusercontent.com/dannguyen/bts-transstats-t100-domestic-demo/master/data/lookup-tables/L_AIRPORT_ID.csv"
local_lookup = "L_AIRPORT_ID.csv"

# Download the lookup CSV if not present
if not os.path.exists(local_lookup):
    print("Downloading L_AIRPORT_ID.csv from GitHub...")
    try:
        urllib.request.urlretrieve(lookup_url, local_lookup)
        print("Download complete.")
    except Exception as e:
        print(f"Error downloading lookup table: {e}")
        exit(1)

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Load L_AIRPORT_ID.csv into a temp list
import csv
lookup_data = []
with open(local_lookup, mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader) # skip header
    for row in reader:
        if len(row) == 2:
            lookup_data.append((row[0], row[1]))

print(f"Loaded {len(lookup_data)} lookup entries.")

# Fetch all airports from airports_raw
cursor.execute("SELECT IATA_CODE, AIRPORT, CITY, STATE FROM airports_raw")
airports = cursor.fetchall()

# We will build a mapping: numeric_code -> IATA_CODE
mapping = {}
unmapped = []

# To make matching robust, clean strings
def clean_str(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

for code, desc in lookup_data:
    # Typical format: "City, ST: Airport Name"
    # Example: "Atlanta, GA: Hartsfield-Jackson Atlanta International"
    city = ""
    state = ""
    airport_name = ""
    
    if ":" in desc:
        city_state, airport_name = desc.split(":", 1)
        if "," in city_state:
            city, state = city_state.split(",", 1)
            city = city.strip()
            state = state.strip()
        airport_name = airport_name.strip()
    else:
        # Fallback if no colon
        airport_name = desc.strip()

    # Find matches in airports_raw
    matches = []
    for iata, name, a_city, a_state in airports:
        # Match by city and state, then check airport name
        if clean_str(a_city) == clean_str(city) and clean_str(a_state) == clean_str(state):
            matches.append((iata, name))
            
    if len(matches) == 1:
        mapping[code] = matches[0][0]
    elif len(matches) > 1:
        # Multiple airports in the same city/state. Match by name.
        best_match = None
        best_score = 0
        clean_desc_name = clean_str(airport_name)
        for iata, name in matches:
            clean_a_name = clean_str(name)
            # Find common substring or inclusion
            if clean_desc_name in clean_a_name or clean_a_name in clean_desc_name:
                mapping[code] = iata
                best_match = iata
                break
        if not best_match:
            # Fallback to first one
            mapping[code] = matches[0][0]
    else:
        # No match by city/state. Try to match by airport name directly.
        clean_desc_name = clean_str(airport_name)
        for iata, name, a_city, a_state in airports:
            clean_a_name = clean_str(name)
            if clean_desc_name in clean_a_name or clean_a_name in clean_desc_name:
                matches.append((iata, name))
        if len(matches) == 1:
            mapping[code] = matches[0][0]
        else:
            unmapped.append((code, desc))

print(f"Mapped {len(mapping)} airport codes.")
print(f"Unmapped codes: {len(unmapped)}")

# Let's insert the mappings into SQLite
cursor.execute("DROP TABLE IF EXISTS airport_mappings")
cursor.execute("""
    CREATE TABLE airport_mappings (
        AIRPORT_ID TEXT PRIMARY KEY,
        IATA_CODE TEXT
    )
""")

# Insert mapped values
cursor.executemany(
    "INSERT OR REPLACE INTO airport_mappings (AIRPORT_ID, IATA_CODE) VALUES (?, ?)",
    [(code, iata) for code, iata in mapping.items()]
)
conn.commit()

# Let's verify how many of the 5-digit codes in flights_raw October can be mapped now
cursor.execute("""
    SELECT COUNT(DISTINCT ORIGIN_AIRPORT) FROM flights_raw 
    WHERE length(ORIGIN_AIRPORT) > 3 
      AND ORIGIN_AIRPORT NOT IN (SELECT AIRPORT_ID FROM airport_mappings)
""")
missing_origin = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(DISTINCT DESTINATION_AIRPORT) FROM flights_raw 
    WHERE length(DESTINATION_AIRPORT) > 3 
      AND DESTINATION_AIRPORT NOT IN (SELECT AIRPORT_ID FROM airport_mappings)
""")
missing_dest = cursor.fetchone()[0]

print(f"Flights with unmapped origin codes: {missing_origin}")
print(f"Flights with unmapped destination codes: {missing_dest}")

# If there are any missing codes, let's print them
if missing_origin > 0:
    cursor.execute("""
        SELECT DISTINCT ORIGIN_AIRPORT FROM flights_raw 
        WHERE length(ORIGIN_AIRPORT) > 3 
          AND ORIGIN_AIRPORT NOT IN (SELECT AIRPORT_ID FROM airport_mappings)
        LIMIT 10
    """)
    print("Sample missing origin codes:", cursor.fetchall())

conn.close()
print("Airport mapping table ready in SQLite!")
