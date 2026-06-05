-- SQL script for U.S. Airline Performance Analysis (EDA & KPIs)

-- 1. Overall Flight Volumes, Cancellations, and Diversions
SELECT
    COUNT(*) AS Total_Flights,
    SUM(CANCELLED) AS Total_Cancellations,
    ROUND(100.0 * SUM(CANCELLED) / COUNT(*), 2) AS Cancellation_Rate_Pct,
    SUM(DIVERTED) AS Total_Diversions,
    ROUND(100.0 * SUM(DIVERTED) / COUNT(*), 2) AS Diversion_Rate_Pct
FROM v_flights_analytical;

-- 2. Cancellations by Reason
SELECT
    coalesce(CANCELLATION_REASON_DESC, 'Unknown/Unspecified') AS Cancellation_Reason,
    COUNT(*) AS Count,
    ROUND(100.0 * COUNT(*) / (SELECT SUM(CANCELLED) FROM v_flights_analytical), 2) AS Share_Pct
FROM v_flights_analytical
WHERE CANCELLED = 1
GROUP BY CANCELLATION_REASON_DESC
ORDER BY Count DESC;

-- 3. Delay Statistics (Departure & Arrival)
SELECT
    ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Departure_Delay,
    MIN(DEPARTURE_DELAY) AS Min_Departure_Delay,
    MAX(DEPARTURE_DELAY) AS Max_Departure_Delay,
    ROUND(AVG(ARRIVAL_DELAY), 2) AS Avg_Arrival_Delay,
    MIN(ARRIVAL_DELAY) AS Min_Arrival_Delay,
    MAX(ARRIVAL_DELAY) AS Max_Arrival_Delay
FROM v_flights_analytical
WHERE CANCELLED = 0 AND DIVERTED = 0;

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
WHERE ARRIVAL_DELAY >= 15 AND CANCELLED = 0 AND DIVERTED = 0;

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
ORDER BY OTP_Rate_Pct DESC;

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
LIMIT 20;

-- 7. KPI Aggregation by Month
SELECT
    MONTH,
    COUNT(*) AS Total_Flights,
    ROUND(100.0 * SUM(CANCELLED) / COUNT(*), 2) AS Cancellation_Rate_Pct,
    ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Departure_Delay,
    ROUND(100.0 * SUM(CASE WHEN ARRIVAL_DELAY <= 15 AND CANCELLED = 0 AND DIVERTED = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS OTP_Rate_Pct
FROM v_flights_analytical
GROUP BY MONTH
ORDER BY MONTH;

-- 8. Day of Week Analysis (1 = Monday, 7 = Sunday - check DOT standard if needed, typically 1=Monday in ISO)
SELECT
    DAY_OF_WEEK,
    COUNT(*) AS Total_Flights,
    ROUND(100.0 * SUM(CANCELLED) / COUNT(*), 2) AS Cancellation_Rate_Pct,
    ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Departure_Delay,
    ROUND(100.0 * SUM(CASE WHEN ARRIVAL_DELAY <= 15 AND CANCELLED = 0 AND DIVERTED = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS OTP_Rate_Pct
FROM v_flights_analytical
GROUP BY DAY_OF_WEEK
ORDER BY DAY_OF_WEEK;

-- 9. Scheduled Departure Hour Analysis
SELECT
    CAST(substr(printf('%04d', cast(SCHEDULED_DEPARTURE as int)), 1, 2) AS INT) AS Departure_Hour,
    COUNT(*) AS Total_Flights,
    ROUND(100.0 * SUM(CANCELLED) / COUNT(*), 2) AS Cancellation_Rate_Pct,
    ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Departure_Delay,
    ROUND(100.0 * SUM(CASE WHEN ARRIVAL_DELAY <= 15 AND CANCELLED = 0 AND DIVERTED = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS OTP_Rate_Pct
FROM v_flights_analytical
GROUP BY Departure_Hour
ORDER BY Departure_Hour;
