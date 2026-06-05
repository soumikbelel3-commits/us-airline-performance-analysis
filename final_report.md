# Capstone Project Report: U.S. Airline Performance & Delay Analysis

**Author:** Antigravity AI Pair Programmer  
**Domain:** Aviation Analytics / Transportation Management  
**Date:** June 6, 2026  

---

## 1. Executive Summary & Introduction

### 1.1 Problem Statement
Flight delays and cancellations represent significant disruptions within the U.S. aviation industry, carrying vast economic consequences for airlines, passengers, and the broader economy. Operational inefficiencies lead to increased fuel burn, wasted crew hours, passenger dissatisfaction, and millions of dollars in lost productivity. This project performs an in-depth, end-to-end data analysis of historical flight records from the U.S. Department of Transportation (DOT) Bureau of Transportation Statistics (BTS) for the year 2015. The dataset covers **5,819,079 domestic flights** operated by 14 major carriers across 322 commercial airports.

### 1.2 Objectives
The primary objectives of this capstone project are:
1. **Design and Implement a Scalable Ingestion Pipeline** to load raw CSV files into an indexed SQL database.
2. **Perform Data Cleaning, Transformation, and Integration** using SQL to handle missing values, format date/time columns, and resolve complex data inconsistencies (such as 5-digit FAA/DOT airport ID mappings).
3. **Formulate Key Performance Indicators (KPIs)** to assess airline and airport operational efficiency.
4. **Conduct Exploratory Data Analysis (EDA)** to isolate key drivers of delays, cancellations, and diversions.
5. **Develop an Interactive, Premium Web Dashboard** using Streamlit and Plotly to enable stakeholders to drill down into metrics.
6. **Provide Data-Driven, Actionable Recommendations** for airlines, airport authorities, and passengers.

---

## 2. Methodology & System Architecture

The project is structured around a multi-stage data pipeline designed for local efficiency and speed:

```
[Raw CSV Files] ---> [Python Chunked Ingest] ---> [SQLite Database] ---> [SQL Cleaning/Indexing]
                                                                                |
[Streamlit Dashboard Web App] <--- [Plotly Visuals] <--- [Analytical Views] <---+
```

### 2.1 Technology Stack
*   **Database Engine:** SQLite 3.x (locally hosted, zero-admin, high-speed relational database).
*   **Data Processing:** Python 3.13 (Pandas for ingestion and cleaning).
*   **SQL Queries:** Advanced SQL scripts utilizing indexing, transactions, common table expressions (CTEs), and relational views.
*   **BI & Visualizations:** Streamlit 1.55 (Python web framework) and Plotly (interactive charts).

### 2.2 Data Ingestion (`ingest.py`)
Because the raw flights dataset is large (~592MB, 5.82 million rows), loading it directly into memory can be highly inefficient. The python script `ingest.py` reads `flights.csv` in chunks of 200,000 rows, inserting them progressively into `flights_raw` in SQLite within a transaction. The lookup tables `airlines.csv` and `airports.csv` are also ingested.

### 2.3 Data Cleaning & Resolution of FAA Numeric Airport Codes
A major challenge in the 2015 BTS dataset is that during the month of **October**, airport codes in the flights table switch from standard 3-letter IATA codes (e.g., `LAX`) to 5-digit U.S. DOT numeric IDs (e.g., `12892`).
To address this, we:
1. Downloaded the official BTS `L_AIRPORT_ID.csv` lookup file.
2. Wrote a Python script `download_and_map_airports.py` to parse these names and match them with `airports.csv` based on city, state, and name text matching.
3. Created an `airport_mappings` table in SQLite to resolve 100% of these 5-digit numeric codes back to standard 3-letter IATA codes.

### 2.4 SQL Views & Indexes (`prepare_data.sql`)
To ensure rapid query responses, we created specific indexes on the raw flights table:
*   `idx_flights_airline` on `AIRLINE`
*   `idx_flights_origin` on `ORIGIN_AIRPORT`
*   `idx_flights_dest` on `DESTINATION_AIRPORT`
*   `idx_flights_month` on `MONTH`
*   `idx_flights_dayofweek` on `DAY_OF_WEEK`

We then defined a virtual analytical view `v_flights_analytical` which integrates the tables and cleans the data on-the-fly:
*   **Date/Time Handling:** Combined `YEAR`, `MONTH`, `DAY` and formatted the `SCHEDULED_DEPARTURE` and `SCHEDULED_ARRIVAL` (which are numeric strings of HHMM like `"0005"`) into standard ISO format (`YYYY-MM-DD HH:MM:SS`).
*   **Missing Values:** Coalesced all null delay minutes (airline, weather, NAS, security, and late aircraft delays) to `0`.
*   **Data Enrichment:** Mapped the character codes in `CANCELLATION_REASON` to descriptive terms: `A -> Carrier`, `B -> Weather`, `C -> National Air System (NAS)`, and `D -> Security`.

---

## 3. Key Performance Indicators (KPIs) Defined

We formulated the following key metrics to monitor operational quality:

1.  **On-Time Performance (OTP) Rate (%):** The percentage of flights arriving at their destination within 15 minutes of their scheduled arrival time.
    $$\text{OTP Rate} = \frac{\text{Flights with (Arrival Delay } \le 15\text{ mins)} \times 100}{\text{Total Scheduled Flights (excluding Cancelled/Diverted)}}$$
2.  **Cancellation Rate (%):** The percentage of scheduled flights that were cancelled.
    $$\text{Cancellation Rate} = \frac{\text{Cancelled Flights} \times 100}{\text{Total Scheduled Flights}}$$
3.  **Average Delay (Minutes):** The average number of minutes of departure and arrival delays (calculated only for flights that actually departed/arrived).
4.  **Percentage Delay Contribution (%):** The proportion of total delay minutes attributed to specific delay types (Airline, Late Aircraft, Weather, Security, or NAS).

---

## 4. Key Findings & Exploratory Data Analysis (EDA)

The SQL scripts in `analysis_queries.sql` were executed against `airline_performance.db` to extract global aviation patterns.

### 4.1 Global Operational Metrics
At a national level, the 2015 domestic flight network performed as follows:

| Metric | Value |
| :--- | :--- |
| **Total Scheduled Flights** | 5,819,079 |
| **Cancelled Flights** | 89,884 (1.54%) |
| **Diverted Flights** | 15,187 (0.26%) |
| **Average Departure Delay** | 9.29 minutes |
| **Average Arrival Delay** | 4.41 minutes |
| **Maximum Departure Delay** | 1,988 minutes (33.1 hours) |

### 4.2 Primary Drivers of Cancellations
Cancellations represent severe disruptions. Out of 89,884 cancellations, the primary reasons are:

| Cancellation Reason | Flight Count | Share (%) |
| :--- | :--- | :--- |
| **Weather** | 48,851 | 54.35% |
| **Carrier (Airline Operations)** | 25,262 | 28.11% |
| **National Air System (NAS)** | 15,749 | 17.52% |
| **Security** | 22 | 0.02% |

*Finding:* Extreme weather is responsible for more than half of all cancellations, followed by airline operational issues (aircraft maintenance, crew logistics).

### 4.3 Attribution of Delay Minutes
When flights are delayed by 15 minutes or more, the delays are categorized by cause. Across **62.65 million total minutes of delays**, the percentage contribution is:

| Delay Cause | Total Delay (Minutes) | Contribution (%) |
| :--- | :--- | :--- |
| **Late Aircraft Delay** | 24,961,900 | 39.84% |
| **Airline (Carrier) Delay** | 20,173,000 | 32.20% |
| **National Air System (NAS)** | 14,335,800 | 22.88% |
| **Weather** | 3,100,230 | 4.95% |
| **Security** | 80,985 | 0.13% |

*Finding:* **Late Aircraft Delay** is the single largest contributor (39.84%). This indicates a severe "network knock-on effect" where a delay on an early flight propagates through the aircraft's schedule for the rest of the day. Directly controlled airline operations (Carrier Delay) are the second largest factor at 32.20%.

---

## 5. Benchmarking & Bottlenecks

### 5.1 Airline Performance Benchmarking
Major carriers exhibited highly contrasting operational efficiencies:

| Rank | Airline (IATA) | Total Flights | Cancelled | Cancel Rate (%) | Avg Dep Delay (min) | Avg Arr Delay (min) | OTP (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Hawaiian (HA)** | 76,272 | 171 | 0.22% | 0.48 | 2.02 | **89.20%** |
| 2 | **Alaska (AS)** | 172,521 | 669 | 0.39% | 1.78 | -0.97 | **87.11%** |
| 3 | **Delta (DL)** | 875,881 | 3,824 | 0.44% | 7.34 | 0.19 | **86.45%** |
| 4 | **American (AA)** | 725,984 | 10,919 | 1.50% | 8.77 | 3.39 | **80.95%** |
| 5 | **Virgin America (VX)** | 61,903 | 534 | 0.86% | 8.95 | 4.69 | **80.61%** |
| 6 | **Southwest (WN)** | 1,261,855 | 16,043 | 1.27% | 10.45 | 4.31 | **80.44%** |
| 7 | **Skywest (OO)** | 588,353 | 9,960 | 1.69% | 7.68 | 5.73 | **80.39%** |
| 8 | **US Airways (US)** | 198,715 | 4,067 | 2.05% | 6.02 | 3.62 | **80.16%** |
| 9 | **United (UA)** | 515,723 | 6,573 | 1.27% | 14.26 | 5.35 | **78.81%** |
| 10 | **Atlantic Southeast (EV)** | 571,977 | 15,231 | 2.66% | 8.49 | 6.39 | **78.57%** |
| 11 | **JetBlue (B6)** | 267,048 | 4,276 | 1.60% | 11.33 | 6.55 | **76.68%** |
| 12 | **American Eagle (MQ)** | 294,632 | 15,025 | 5.10% | 9.63 | 6.11 | **74.73%** |
| 13 | **Frontier (F9)** | 90,836 | 588 | 0.65% | 13.27 | 12.40 | **74.02%** |
| 14 | **Spirit (NK)** | 117,379 | 2,004 | 1.71% | 15.68 | 14.20 | **69.88%** |

*Finding:*
*   **Leaders:** Hawaiian Airlines leads with 89.20% OTP, followed closely by Alaska (87.11%) and Delta (86.45%). Notably, Alaska's average arrival delay is negative (-0.97 minutes), indicating that they consistently arrive *ahead* of schedule.
*   **Laggards:** Spirit Airlines is the worst performing airline with an OTP of only 69.88% and a high average arrival delay of 14.20 minutes. Frontier also struggles with 74.02% OTP.
*   **Cancellations:** American Eagle (MQ) has a massive 5.10% cancellation rate, meaning 1 in 20 of their scheduled flights is cancelled, a severe outlier.

### 5.2 Airport Bottlenecks (Top 20 Hubs)
Analyzing the top 20 busiest airports in the United States highlights critical network bottlenecks:

*   **Best Major Hubs:** **Salt Lake City (SLC)** leads major airports with a remarkable **86.86% OTP** and an average departure delay of only 4.46 minutes. **Minneapolis-St. Paul (MSP)** and **Seattle (SEA)** also show stellar efficiency at ~84% OTP.
*   **Worst Bottlenecks:** **LaGuardia (LGA)** in New York has the worst cancellation rate among major hubs at **4.30%** and a low OTP of 73.79%. **Chicago O'Hare (ORD)** is another major friction point, with a **2.74% cancellation rate** and an average departure delay of **12.96 minutes**, dragging its OTP down to 75.27%.

---

## 6. Temporal Patterns in Operations

Delays and cancellations are highly sensitive to seasonal and daily schedules:

### 6.1 Monthly Seasonal Trends
*   **Worst Cancellations:** **February** exhibits a massive **4.78% cancellation rate**, driven entirely by severe winter storms.
*   **Worst Delays:** **June** has the highest average departure delays (**13.74 minutes**), caused by a combination of high passenger volumes (summer travel) and severe summer thunderstorms.
*   **Best Month:** **September and October** are the most reliable months, with OTP rates peaking at **87%** and cancellation rates dropping to less than 0.50% (often called the "golden travel window" when weather is stable and traffic dips).

### 6.2 Day of Week Trends
*   **Best Day:** **Saturday** is by far the most reliable day to travel, achieving **83.32% OTP** and the lowest average departure delay (7.73 minutes). This is due to reduced business travel and lower overall flight frequencies.
*   **Worst Day:** **Monday** is the worst day, with a **2.43% cancellation rate** and average departure delays of 10.62 minutes, caused by the morning corporate travel rush.

### 6.3 Time of Day Trends
*   **Morning Reliability:** Flights departing between **5:00 AM and 7:00 AM** are highly reliable, achieving over **89% to 91% OTP** and average delays of less than 2.5 minutes.
*   **Evening Delay Peak:** Delays accumulate steadily throughout the day. The worst time to depart is between **6:00 PM and 8:00 PM**, where OTP drops to **72.8%** and average departure delays peak at **15.00 minutes**. This is a direct consequence of the "late aircraft" propagation effect.

---

## 7. Dashboard Walkthrough & Features

The Streamlit web application `app.py` has been successfully developed and is running locally on **`http://localhost:8501`**. 

### 7.1 Key Sections
1.  **Overview Dashboard:** Features high-impact KPI metric cards (Total Flights, OTP %, Cancellation %, Avg Delay), a donut chart showing cancellation reasons, and a bar chart showing the absolute minutes of delay categories.
2.  **Airline Performance:** Displays a benchmarking table for all 14 airlines. It features interactive horizontal bar charts comparing OTP and average arrival delay side-by-side.
3.  **Airport Analysis:** Features an **interactive map** displaying the top 50 U.S. airports. Bubbles are sized by total flight volume and colored using a Red-Yellow-Green gradient representing OTP. Side panels show the worst airports for delays and cancellations.
4.  **Temporal Trends:** Line charts showing monthly volume vs. OTP, daily line trends, and an hourly line chart mapping delay buildup throughout the day.
5.  **SQL Playground:** An embedded developer environment allowing users to run arbitrary SQL queries on the SQLite database, displaying the results in real-time with the ability to download the output as a CSV.

---

## 8. Actionable Recommendations

### 8.1 For Airlines
*   **Buffer Time Optimizations:** Since "Late Aircraft Delay" is the largest cause of delays (39.84%), airlines must build more realistic turnaround buffer times, particularly for aircraft scheduled for more than 4 flights a day.
*   **Targeted Schedule Reductions during Summer Peaks:** Airlines should slightly trim frequencies during peak summer hours (June) to prevent localized cascading delays, replacing multiple smaller regional jets with larger mainline aircraft to keep passenger throughput high.

### 8.2 For Airport Authorities
*   **De-icing and Winter Readiness (Midwest & Northeast):** Airports like ORD and LGA must review winter weather response protocols to mitigate the severe spike in February cancellations (4.78%).
*   **Slot Management at LGA and ORD:** Establish stricter slot limits during peak corporate travel hours (Mondays) to prevent runaway runway queues and ground holds that drive NAS delays.

### 8.3 For Passengers
*   **Fly Early:** Book flights departing before 8:00 AM. These flights have a >90% chance of being on time, as aircraft are already at the gate and the network hasn't had time to build up delay cascades.
*   **Travel on Saturdays:** Saturday departures are significantly less delayed than weekdays.
*   **Carrier Selection:** Prioritize Hawaiian, Alaska, or Delta. Avoid Spirit, Frontier, and American Eagle for time-critical travel.

---

## 9. Conclusion & Limitations

### 9.1 Conclusion
This project successfully completed a comprehensive U.S. Airline Performance & Delay capstone. Through database indexing and data mapping, we resolved the October numeric FAA code anomaly and created a highly responsive database. The Streamlit dashboard provides an intuitive, high-performance BI tool, and our analysis has identified late aircraft cascades, February winter storms, and evening departures as the primary bottlenecks in the U.S. aviation network.

### 9.2 Limitations
*   **Temporal Scope:** The dataset is limited to the year 2015. While representative, it does not reflect recent shifts in carrier market share or post-pandemic schedule changes.
*   **Lack of International Flights:** The analysis is restricted to domestic flights; international routes operate under different slot restrictions and custom procedures.
*   **Missing Passenger Data:** The dataset lacks passenger load factors (occupancy), which prevents calculating the exact passenger-hour impact of delays.
