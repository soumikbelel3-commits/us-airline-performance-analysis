# U.S. Airline Performance & Delay Analysis
### Capstone Project Presentation
**Presented by:** Antigravity AI Pair Programmer  
**Date:** June 6, 2026  

---

## 1. Executive Summary & Problem Statement

*   **The Problem:** Flight disruptions (delays, cancellations, diversions) carry massive economic and operational consequences.
*   **The Scope:** Analysed **5,819,079 domestic flights** in the U.S. for 2015, covering 14 airlines and 322 airports.
*   **Key Questions Answered:**
    *   What are the primary drivers of delays and cancellations?
    *   Which airlines and airports are the most and least efficient?
    *   How do temporal factors (month, day, hour) affect network reliability?
    *   What actionable steps can stakeholders take to improve operations?

---

## 2. Methodology & Database Design

*   **Database Stack:** SQLite 3.x for database storage; Python/Pandas for chunked CSV ingestion (~2.5 minutes total runtime).
*   **Data Cleaning Challenges Resolved:**
    *   *FAA Numeric Code Mapping:* In October 2015, flight records switched to 5-digit DOT IDs. We parsed and mapped 100% of these back to standard 3-letter IATA codes.
    *   *Null Value Handling:* Coalesced all missing delay metrics to `0`.
    *   *Date/Time Parsing:* Formatted raw departure/arrival strings (HHMM) into standard datetimes.
*   **Optimization:** Configured database indexes on airline, airport, and month fields, reducing query runtimes from seconds to milliseconds.

---

## 3. Key Performance Indicators (KPIs)

To evaluate efficiency, we defined and calculated four core KPIs:

1.  **On-Time Performance (OTP) Rate:** Flights arriving within 15 minutes of scheduled time.
2.  **Cancellation Rate (%):** Percentage of scheduled flights cancelled.
3.  **Average Delay (Minutes):** Mean departure/arrival delays.
4.  **Percentage Delay Contribution:** Share of delay minutes by cause (Weather, Carrier, Late Aircraft, NAS, Security).

---

## 4. Overall Flight Metrics (2015)

*   **Total Scheduled Flights:** 5,819,079
*   **Cancellation Rate:** 1.54% (89,884 flights)
*   **Diversion Rate:** 0.26% (15,187 flights)
*   **Average Departure Delay:** 9.29 minutes
*   **Average Arrival Delay:** 4.41 minutes
*   **Worst-Case Delay:** 1,988 minutes (33.1 hours) departure delay

---

## 5. What Causes Cancellations?

Analysis of the 89,884 cancelled flights reveals weather as the dominant driver:

*   **Weather:** **54.35%** (48,851 flights)
    *   *Takeaway:* Heavy snowstorms, winter weather, and summer thunderstorms are the single largest operational blocker.
*   **Carrier (Airline Operations):** **28.11%** (25,262 flights)
    *   *Takeaway:* Crew scheduling failures and aircraft maintenance issues.
*   **National Air System (NAS):** **17.52%** (15,749 flights)
    *   *Takeaway:* Air traffic control volume holds and runway congestion.
*   **Security:** **0.02%** (22 flights)

---

## 6. What Causes Delays?

Across **62.65 million total minutes of delayed arrivals** (flights delayed $\ge 15$ mins), the breakdown is:

*   **Late Aircraft Delay:** **39.84%** (24.96 million mins)
    *   *The "cascading effect":* A delay on an early flight propagates to subsequent flights using that same plane.
*   **Airline (Carrier) Delay:** **32.20%** (20.17 million mins)
    *   *Control factor:* Under direct control of the airline (gate hold, maintenance, bag loading).
*   **National Air System (NAS) Delay:** **22.88%** (14.33 million mins)
    *   *Airports/ATC:* Airport congestion, runway delays.
*   **Weather Delay:** **4.95%** (3.10 million mins)
*   **Security Delay:** **0.13%** (80,985 mins)

---

## 7. Airline Benchmarking (The Leaders)

Contrasting performance across the 14 major carriers:

*   **Hawaiian Airlines (HA):** **89.20% OTP** (Rank 1)
    *   *Why:* Favourable local weather, point-to-point shuttle operations.
*   **Alaska Airlines (AS):** **87.11% OTP** (Rank 2)
    *   *Highlight:* Average arrival delay of **-0.97 minutes** (on average, they arrive early!).
*   **Delta Air Lines (DL):** **86.45% OTP** (Rank 3)
    *   *Highlight:* The best performer among the "Big Three" legacy carriers, with a low 0.44% cancellation rate.

---

## 8. Airline Benchmarking (The Laggards)

*   **Spirit Airlines (NK):** **69.88% OTP** (Worst)
    *   *Metrics:* Average departure delay of 15.68 minutes; average arrival delay of 14.20 minutes.
*   **Frontier Airlines (F9):** **74.02% OTP** (Rank 13)
    *   *Metrics:* Average departure delay of 13.27 minutes.
*   **American Eagle (MQ):** **74.73% OTP** (Rank 12)
    *   *Severe Outlier:* **5.10% cancellation rate** (1 in 20 flights cancelled). Indicates severe regional crew and aircraft constraints.

---

## 9. Airport Performance & Bottlenecks

An analysis of the top 20 busiest U.S. airports identifies major friction points:

*   **The Most Efficient Hub:**
    *   **Salt Lake City (SLC):** **86.86% OTP**, 0.38% Cancellation, 4.46 min average departure delay.
    *   *Minneapolis-St. Paul (MSP):* **84.06% OTP**.
*   **Major Congestion Bottlenecks:**
    *   **LaGuardia (LGA):** **4.30% Cancellation Rate** and 73.79% OTP.
    *   **Chicago O'Hare (ORD):** **2.74% Cancellation Rate** and 12.96 min average departure delay.
    *   *Newark (EWR):* **2.88% Cancellation Rate** and 12.81 min average departure delay.

---

## 10. Temporal Trends (Seasonal & Daily)

*   **Monthly Seasonal Patterns:**
    *   *Cancellations:* Peak in **February (4.78%)** due to winter blizzards.
    *   *Delays:* Peak in **June (13.74 min average)** due to summer vacation volumes and thunderstorms.
    *   *Best Months:* **September (87.02% OTP)** and **October (87.55% OTP)**.
*   **Day of Week Patterns:**
    *   *Best Day:* **Saturday (83.32% OTP)**. Low traffic, minimal business travel.
    *   *Worst Day:* **Monday (78.71% OTP)**. Corporate travel morning peak.

---

## 11. Hour of Day Delay Accumulation

Delays build up progressively as planes fly multiple legs throughout the day:

*   **Morning (5:00 AM - 7:00 AM):**
    *   Highly reliable: **91.20% OTP** (5 AM) and **89.53% OTP** (6 AM).
    *   Average departure delays are under 2.5 minutes.
*   **Evening (6:00 PM - 8:00 PM):**
    *   OTP drops to **72.81%** (8 PM).
    *   Average departure delays peak at **15.00 minutes**.
    *   *Cause:* Cascading aircraft arrivals ("Late Aircraft" propagation).

---

## 12. Streamlit Dashboard Features

The running interactive dashboard (**`http://localhost:8501`**) provides:

1.  **Overview Panel:** High-level metrics, cancellation reason pie charts, and delay cause charts.
2.  **Airline Benchmarking:** Parallel bar charts for visual comparison of OTP and delays.
3.  **Airport Analysis Map:** Interactive geographical map of U.S. airports. Bubbles are sized by volume and colored by OTP (Red-Yellow-Green).
4.  **Temporal Trends:** Line charts mapping month, day, and hourly curves.
5.  **SQL Playground:** Execute custom SQL queries directly against `airline_performance.db` with CSV download options.

---

## 13. Actionable Recommendations

*   **For Airlines:**
    *   *Turnaround Buffers:* Allocate larger buffer times between flights later in the day to break the "late aircraft" propagation loop.
    *   *Trim Summer Schedules:* Slightly decrease flight frequencies in June to prevent systemic delays.
*   **For Airports:**
    *   *Winter Response:* LGA and ORD must improve winter operations (snow removal) to address February cancellation spikes.
    *   *Slot Controls:* Tighten flight arrivals during Monday morning rush hours to prevent runway queuing.
*   **For Passengers:**
    *   *Book Morning Flights:* Depart before 8:00 AM to ensure >90% on-time rates.
    *   *Choose AS/DL/HA:* Avoid NK, F9, and MQ if schedule is tight.
    *   *Fly Saturdays:* Avoid Monday travel to sidestep peak delays.
