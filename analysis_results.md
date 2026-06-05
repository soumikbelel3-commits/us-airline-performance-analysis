# SQL Analytical Query Results

This file contains the output tables of the analytical queries executed on `airline_performance.db`.

## 1. Overall Flight Volumes, Cancellations, and Diversions

```sql
-- SQL script for U.S. Airline Performance Analysis (EDA & KPIs)

-- 1. Overall Flight Volumes, Cancellations, and Diversions
SELECT
    COUNT(*) AS Total_Flights,
    SUM(CANCELLED) AS Total_Cancellations,
    ROUND(100.0 * SUM(CANCELLED) / COUNT(*), 2) AS Cancellation_Rate_Pct,
    SUM(DIVERTED) AS Total_Diversions,
    ROUND(100.0 * SUM(DIVERTED) / COUNT(*), 2) AS Diversion_Rate_Pct
FROM v_flights_analytical
```

### Results:

|   Total_Flights |   Total_Cancellations |   Cancellation_Rate_Pct |   Total_Diversions |   Diversion_Rate_Pct |
|----------------:|----------------------:|------------------------:|-------------------:|---------------------:|
|     5.81908e+06 |                 89884 |                    1.54 |              15187 |                 0.26 |

## 2. Cancellations by Reason

```sql
-- 2. Cancellations by Reason
SELECT
    coalesce(CANCELLATION_REASON_DESC, 'Unknown/Unspecified') AS Cancellation_Reason,
    COUNT(*) AS Count,
    ROUND(100.0 * COUNT(*) / (SELECT SUM(CANCELLED) FROM v_flights_analytical), 2) AS Share_Pct
FROM v_flights_analytical
WHERE CANCELLED = 1
GROUP BY CANCELLATION_REASON_DESC
ORDER BY Count DESC
```

### Results:

| Cancellation_Reason       |   Count |   Share_Pct |
|:--------------------------|--------:|------------:|
| Weather                   |   48851 |       54.35 |
| Carrier                   |   25262 |       28.11 |
| National Air System (NAS) |   15749 |       17.52 |
| Security                  |      22 |        0.02 |

## 3. Delay Statistics (Departure & Arrival)

```sql
-- 3. Delay Statistics (Departure & Arrival)
SELECT
    ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Departure_Delay,
    MIN(DEPARTURE_DELAY) AS Min_Departure_Delay,
    MAX(DEPARTURE_DELAY) AS Max_Departure_Delay,
    ROUND(AVG(ARRIVAL_DELAY), 2) AS Avg_Arrival_Delay,
    MIN(ARRIVAL_DELAY) AS Min_Arrival_Delay,
    MAX(ARRIVAL_DELAY) AS Max_Arrival_Delay
FROM v_flights_analytical
WHERE CANCELLED = 0 AND DIVERTED = 0
```

### Results:

|   Avg_Departure_Delay |   Min_Departure_Delay |   Max_Departure_Delay |   Avg_Arrival_Delay |   Min_Arrival_Delay |   Max_Arrival_Delay |
|----------------------:|----------------------:|----------------------:|--------------------:|--------------------:|--------------------:|
|                  9.29 |                   -82 |                  1988 |                4.41 |                 -87 |                1971 |

## 4. Distribution of Delay Types

```sql
-- 4. Distribution of Delay Types (Percentage Contribution to Total Delay Minutes)
SELECT
    SUM(AIRLINE_DELAY) AS Total_Airline_Delay_Mins,
    ROUND(100.0 * SUM(AIRLINE_DELAY) / (SUM(AIRLINE_DELAY) + SUM(WEATHER_DELAY) + SUM(AIR_SYSTEM_DELAY) + SUM(SECURITY_DELAY) + SUM(LATE_AIRCRAFT_DELAY)), 2) AS Airline_Share_Pct,
    SUM(WEATHER_DELAY) AS Total_Weather_Delay_Mins,
    ROUND(100.0 * SUM(WEATHER_DELAY) / (SUM(AIRLINE_DELAY) + SUM(WEATHER_DELAY) + SUM(AIR_SYSTEM_DELAY) + SUM(SECURITY_DELAY) + SUM(LATE_AIRCRAFT_DELAY)), 2) AS Weather_Share_Pct,
    SUM(AIR_SYSTEM_DELAY) AS Total_NAS_Delay_Mins,
    ROUND(100.0 * SUM(AIR_SYSTEM_DELAY) / (SUM(AIRLINE_DELAY) + SUM(WEATHER_DELAY) + SUM(AIR_SYSTEM_DELAY) + SUM(SECURITY_DELAY) + SUM(LATE_AIRCRAFT_DELAY)), 2) AS NAS_Share_Pct,
    SUM(SECURITY_DELAY) AS Total_Security_Delay_Mins,
    ROUND(100.0 * SUM(SECURITY_DELAY) / (SUM(AIRLINE_DELAY) + SUM(WEATHER_DELAY) + SUM(AIR_SYSTEM_DELAY) + SUM(SECURITY_DELAY) + SUM(LATE_AIRCRAFT_DELAY)), 2) AS Security_Share_Pct,
    SUM(LATE_AIRCRAFT_DELAY) AS Total_Late_Aircraft_Delay_Mins,
    ROUND(100.0 * SUM(LATE_AIRCRAFT_DELAY) / (SUM(AIRLINE_DELAY) + SUM(WEATHER_DELAY) + SUM(AIR_SYSTEM_DELAY) + SUM(SECURITY_DELAY) + SUM(LATE_AIRCRAFT_DELAY)), 2) AS Late_Aircraft_Share_Pct
FROM v_flights_analytical
WHERE ARRIVAL_DELAY >= 15 AND CANCELLED = 0 AND DIVERTED = 0
```

### Results:

|   Total_Airline_Delay_Mins |   Airline_Share_Pct |   Total_Weather_Delay_Mins |   Weather_Share_Pct |   Total_NAS_Delay_Mins |   NAS_Share_Pct |   Total_Security_Delay_Mins |   Security_Share_Pct |   Total_Late_Aircraft_Delay_Mins |   Late_Aircraft_Share_Pct |
|---------------------------:|--------------------:|---------------------------:|--------------------:|-----------------------:|----------------:|----------------------------:|---------------------:|---------------------------------:|--------------------------:|
|                 2.0173e+07 |                32.2 |                3.10023e+06 |                4.95 |            1.43358e+07 |           22.88 |                       80985 |                 0.13 |                      2.49619e+07 |                     39.84 |

## 5. KPI Aggregation by Airline

```sql
-- 5. KPI Aggregation by Airline
SELECT
    AIRLINE_CODE,
    AIRLINE_NAME,
    COUNT(*) AS Total_Flights,
    SUM(CANCELLED) AS Cancelled_Flights,
    ROUND(100.0 * SUM(CANCELLED) / COUNT(*), 2) AS Cancellation_Rate_Pct,
    ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Departure_Delay,
    ROUND(AVG(ARRIVAL_DELAY), 2) AS Avg_Arrival_Delay,
    SUM(CASE WHEN ARRIVAL_DELAY <= 15 AND CANCELLED = 0 AND DIVERTED = 0 THEN 1 ELSE 0 END) AS On_Time_Arrivals,
    ROUND(100.0 * SUM(CASE WHEN ARRIVAL_DELAY <= 15 AND CANCELLED = 0 AND DIVERTED = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS OTP_Rate_Pct
FROM v_flights_analytical
GROUP BY AIRLINE_CODE, AIRLINE_NAME
ORDER BY OTP_Rate_Pct DESC
```

### Results:

| AIRLINE_CODE   | AIRLINE_NAME                 |   Total_Flights |   Cancelled_Flights |   Cancellation_Rate_Pct |   Avg_Departure_Delay |   Avg_Arrival_Delay |   On_Time_Arrivals |   OTP_Rate_Pct |
|:---------------|:-----------------------------|----------------:|--------------------:|------------------------:|----------------------:|--------------------:|-------------------:|---------------:|
| HA             | Hawaiian Airlines Inc.       |           76272 |                 171 |                    0.22 |                  0.48 |                2.02 |              68031 |          89.2  |
| AS             | Alaska Airlines Inc.         |          172521 |                 669 |                    0.39 |                  1.78 |               -0.97 |             150277 |          87.11 |
| DL             | Delta Air Lines Inc.         |          875881 |                3824 |                    0.44 |                  7.34 |                0.19 |             757163 |          86.45 |
| AA             | American Airlines Inc.       |          725984 |               10919 |                    1.5  |                  8.77 |                3.39 |             587697 |          80.95 |
| VX             | Virgin America               |           61903 |                 534 |                    0.86 |                  8.95 |                4.69 |              49900 |          80.61 |
| WN             | Southwest Airlines Co.       |         1261855 |               16043 |                    1.27 |                 10.45 |                4.31 |            1015086 |          80.44 |
| OO             | Skywest Airlines Inc.        |          588353 |                9960 |                    1.69 |                  7.68 |                5.73 |             472964 |          80.39 |
| US             | US Airways Inc.              |          198715 |                4067 |                    2.05 |                  6.02 |                3.62 |             159293 |          80.16 |
| UA             | United Air Lines Inc.        |          515723 |                6573 |                    1.27 |                 14.26 |                5.35 |             406459 |          78.81 |
| EV             | Atlantic Southeast Airlines  |          571977 |               15231 |                    2.66 |                  8.49 |                6.39 |             449421 |          78.57 |
| B6             | JetBlue Airways              |          267048 |                4276 |                    1.6  |                 11.33 |                6.55 |             204785 |          76.68 |
| MQ             | American Eagle Airlines Inc. |          294632 |               15025 |                    5.1  |                  9.63 |                6.11 |             220168 |          74.73 |
| F9             | Frontier Airlines Inc.       |           90836 |                 588 |                    0.65 |                 13.27 |               12.4  |              67239 |          74.02 |
| NK             | Spirit Air Lines             |          117379 |                2004 |                    1.71 |                 15.68 |               14.2  |              82027 |          69.88 |

## 6. KPI Aggregation by Origin Airport (Top 20 by Volume)

```sql
-- 6. KPI Aggregation by Origin Airport (Top 20 by Volume)
SELECT
    ORIGIN_AIRPORT AS Airport_Code,
    ORIGIN_AIRPORT_NAME AS Airport_Name,
    ORIGIN_CITY AS City,
    ORIGIN_STATE AS State,
    COUNT(*) AS Total_Flights,
    ROUND(100.0 * SUM(CANCELLED) / COUNT(*), 2) AS Cancellation_Rate_Pct,
    ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Departure_Delay,
    ROUND(100.0 * SUM(CASE WHEN ARRIVAL_DELAY <= 15 AND CANCELLED = 0 AND DIVERTED = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS OTP_Rate_Pct
FROM v_flights_analytical
GROUP BY ORIGIN_AIRPORT, ORIGIN_AIRPORT_NAME, ORIGIN_CITY, ORIGIN_STATE
ORDER BY Total_Flights DESC
LIMIT 20
```

### Results:

| Airport_Code   | Airport_Name                                                           | City              | State   |   Total_Flights |   Cancellation_Rate_Pct |   Avg_Departure_Delay |   OTP_Rate_Pct |
|:---------------|:-----------------------------------------------------------------------|:------------------|:--------|----------------:|------------------------:|----------------------:|---------------:|
| ATL            | Hartsfield-Jackson Atlanta International Airport                       | Atlanta           | GA      |          379424 |                    0.68 |                  8.84 |          84.05 |
| ORD            | Chicago O'Hare International Airport                                   | Chicago           | IL      |          313536 |                    2.74 |                 12.96 |          75.27 |
| DFW            | Dallas/Fort Worth International Airport                                | Dallas-Fort Worth | TX      |          260595 |                    2.56 |                 10.89 |          77.48 |
| DEN            | Denver International Airport                                           | Denver            | CO      |          214191 |                    1.01 |                 11.22 |          78.22 |
| LAX            | Los Angeles International Airport                                      | Los Angeles       | CA      |          212401 |                    1.05 |                 10.11 |          79.39 |
| SFO            | San Francisco International Airport                                    | San Francisco     | CA      |          162178 |                    1.36 |                 10.62 |          79.49 |
| PHX            | Phoenix Sky Harbor International Airport                               | Phoenix           | AZ      |          159736 |                    0.58 |                  8.3  |          81.74 |
| IAH            | George Bush Intercontinental Airport                                   | Houston           | TX      |          146622 |                    1.45 |                 11.42 |          78.05 |
| LAS            | McCarran International Airport                                         | Las Vegas         | NV      |          145869 |                    0.66 |                 10.5  |          79.86 |
| MSP            | Minneapolis-Saint Paul International Airport                           | Minneapolis       | MN      |          122701 |                    0.67 |                  6.87 |          84.06 |
| SEA            | Seattle-Tacoma International Airport                                   | Seattle           | WA      |          121287 |                    0.39 |                  6.51 |          83.82 |
| MCO            | Orlando International Airport                                          | Orlando           | FL      |          120029 |                    0.95 |                 11.4  |          79.93 |
| DTW            | Detroit Metropolitan Airport                                           | Detroit           | MI      |          118425 |                    1.09 |                  8.71 |          82.34 |
| BOS            | Gen. Edward Lawrence Logan International Airport                       | Boston            | MA      |          118011 |                    2.29 |                  9.01 |          78.91 |
| EWR            | Newark Liberty International Airport                                   | Newark            | NJ      |          111394 |                    2.88 |                 12.81 |          77.2  |
| CLT            | Charlotte Douglas International Airport                                | Charlotte         | NC      |          109896 |                    1    |                  8.03 |          79.62 |
| LGA            | LaGuardia Airport (Marine Air Terminal)                                | New York          | NY      |          108195 |                    4.3  |                 12.23 |          73.79 |
| SLC            | Salt Lake City International Airport                                   | Salt Lake City    | UT      |          105973 |                    0.38 |                  4.46 |          86.86 |
| JFK            | John F. Kennedy International Airport (New York International Airport) | New York          | NY      |          102114 |                    1.91 |                 11.54 |          77.44 |
| BWI            | Baltimore-Washington International Airport                             | Baltimore         | MD      |           94101 |                    1.65 |                 12.69 |          77.37 |

## 7. KPI Aggregation by Month

```sql
-- 7. KPI Aggregation by Month
SELECT
    MONTH,
    COUNT(*) AS Total_Flights,
    ROUND(100.0 * SUM(CANCELLED) / COUNT(*), 2) AS Cancellation_Rate_Pct,
    ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Departure_Delay,
    ROUND(100.0 * SUM(CASE WHEN ARRIVAL_DELAY <= 15 AND CANCELLED = 0 AND DIVERTED = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS OTP_Rate_Pct
FROM v_flights_analytical
GROUP BY MONTH
ORDER BY MONTH
```

### Results:

|   MONTH |   Total_Flights |   Cancellation_Rate_Pct |   Avg_Departure_Delay |   OTP_Rate_Pct |
|--------:|----------------:|------------------------:|----------------------:|---------------:|
|       1 |          469968 |                    2.55 |                  9.52 |          77.58 |
|       2 |          429191 |                    4.78 |                 11.33 |          73.6  |
|       3 |          504312 |                    2.18 |                  9.46 |          79.39 |
|       4 |          485151 |                    0.93 |                  7.65 |          82.55 |
|       5 |          496993 |                    1.15 |                  9.35 |          81.15 |
|       6 |          503897 |                    1.81 |                 13.74 |          75.57 |
|       7 |          520718 |                    0.92 |                 11.3  |          78.82 |
|       8 |          510536 |                    0.99 |                  9.84 |          80.93 |
|       9 |          464946 |                    0.45 |                  4.8  |          87.02 |
|      10 |          486165 |                    0.5  |                  4.96 |          87.55 |
|      11 |          467972 |                    0.98 |                  6.88 |          84.36 |
|      12 |          479230 |                    1.68 |                 11.59 |          78.54 |

## 8. Day of Week Analysis

```sql
-- 8. Day of Week Analysis (1 = Monday, 7 = Sunday - check DOT standard if needed, typically 1=Monday in ISO)
SELECT
    DAY_OF_WEEK,
    COUNT(*) AS Total_Flights,
    ROUND(100.0 * SUM(CANCELLED) / COUNT(*), 2) AS Cancellation_Rate_Pct,
    ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Departure_Delay,
    ROUND(100.0 * SUM(CASE WHEN ARRIVAL_DELAY <= 15 AND CANCELLED = 0 AND DIVERTED = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS OTP_Rate_Pct
FROM v_flights_analytical
GROUP BY DAY_OF_WEEK
ORDER BY DAY_OF_WEEK
```

### Results:

|   DAY_OF_WEEK |   Total_Flights |   Cancellation_Rate_Pct |   Avg_Departure_Delay |   OTP_Rate_Pct |
|--------------:|----------------:|------------------------:|----------------------:|---------------:|
|             1 |          865543 |                    2.43 |                 10.62 |          78.71 |
|             2 |          844600 |                    1.78 |                  9.01 |          80.71 |
|             3 |          855897 |                    1.25 |                  8.54 |          81.28 |
|             4 |          872521 |                    1.41 |                  9.82 |          79.39 |
|             5 |          862209 |                    1.02 |                  9.34 |          80.54 |
|             6 |          700545 |                    1.25 |                  7.73 |          83.32 |
|             7 |          817764 |                    1.61 |                  9.26 |          80.84 |

## 9. Scheduled Departure Hour Analysis

```sql
-- 9. Scheduled Departure Hour Analysis
SELECT
    CAST(substr(printf('%04d', cast(SCHEDULED_DEPARTURE as int)), 1, 2) AS INT) AS Departure_Hour,
    COUNT(*) AS Total_Flights,
    ROUND(100.0 * SUM(CANCELLED) / COUNT(*), 2) AS Cancellation_Rate_Pct,
    ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Departure_Delay,
    ROUND(100.0 * SUM(CASE WHEN ARRIVAL_DELAY <= 15 AND CANCELLED = 0 AND DIVERTED = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS OTP_Rate_Pct
FROM v_flights_analytical
GROUP BY Departure_Hour
ORDER BY Departure_Hour
```

### Results:

|   Departure_Hour |   Total_Flights |   Cancellation_Rate_Pct |   Avg_Departure_Delay |   OTP_Rate_Pct |
|-----------------:|----------------:|------------------------:|----------------------:|---------------:|
|                0 |           14664 |                    0.85 |                  7.14 |          83.89 |
|                1 |            5159 |                    1.05 |                  8.01 |          80.91 |
|                2 |            1414 |                    1.98 |                  7.12 |          81.68 |
|                3 |             778 |                    1.41 |                  8.79 |          81.75 |
|                4 |             531 |                    0.56 |                 10.28 |          80.23 |
|                5 |          118051 |                    1.75 |                  1.86 |          91.2  |
|                6 |          406940 |                    1.8  |                  2.07 |          89.53 |
|                7 |          393947 |                    1.33 |                  3.21 |          87.93 |
|                8 |          381014 |                    1.4  |                  4.62 |          86.29 |
|                9 |          351403 |                    1.23 |                  5.61 |          85.16 |
|               10 |          371644 |                    1.28 |                  6.81 |          83.94 |
|               11 |          358084 |                    1.27 |                  7.69 |          82.99 |
|               12 |          355611 |                    1.34 |                  8.84 |          81.78 |
|               13 |          363509 |                    1.3  |                  9.68 |          80.43 |
|               14 |          329715 |                    1.47 |                 11.02 |          78.51 |
|               15 |          367760 |                    1.43 |                 11.78 |          77.9  |
|               16 |          334153 |                    1.69 |                 12.72 |          76.15 |
|               17 |          390362 |                    1.74 |                 13.61 |          74.8  |
|               18 |          334380 |                    1.94 |                 14.71 |          73.25 |
|               19 |          331338 |                    1.85 |                 14.81 |          72.99 |
|               20 |          259432 |                    2.02 |                 15    |          72.81 |
|               21 |          187467 |                    1.96 |                 13.46 |          74.77 |
|               22 |          117551 |                    1.73 |                 11.58 |          76.45 |
|               23 |           44172 |                    1.01 |                  9.43 |          80.62 |

