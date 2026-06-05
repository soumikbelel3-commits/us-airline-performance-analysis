# U.S. Airline Performance & Delay Analysis

An end-to-end data engineering and business intelligence capstone project. This project ingests, cleans, and analyzes a dataset of **5.8 million domestic U.S. flights (2015)** to uncover drivers of delays/cancellations, benchmark carrier/airport performance, and present findings in an interactive, high-performance web dashboard.

---

## 🚀 Key Features

*   **Scalable SQL Ingestion Pipeline:** Chunked CSV loading into SQLite utilizing database transactions for memory-efficient loading under 2.5 minutes.
*   **Automated Data Cleaning & Mapping:** Resolves a major dataset anomaly where all October flight records use 5-digit U.S. DOT numeric IDs instead of standard IATA 3-letter codes. Achieve 100% resolution using an automated string-matching mapping script.
*   **Performance Optimization (OLAP Cubes):** Implements a pre-aggregated database summary table design pattern, reducing dashboard SQL query runtimes from 28+ seconds to **under 10 milliseconds**.
*   **Interactive BI Dashboard:** A multi-page Streamlit application featuring:
    *   *Overview:* High-level KPI metric cards (OTP, cancellations, delay minutes breakdown).
    *   *Airline Benchmarking:* Interactive parallel bar charts comparing carrier OTP and delays.
    *   *Airport Analysis:* U.S. geographic map of airport traffic and OTP, alongside list of delay bottlenecks.
    *   *Temporal Trends:* Volumetric and performance trends by month, day, and hour.
    *   *SQL Playground:* Embedded SQL query editor to run custom queries directly against the database with CSV export.
*   **Comprehensive Documentation:** Includes a deep-dive analytical report and a stakeholder slide presentation.

---

## 📂 Project Structure

```
├── ingest.py                    # Chunked raw ingestion of CSV files to SQLite
├── download_and_map_airports.py # Downloads L_AIRPORT_ID lookup and maps October FAA codes
├── prepare_data.sql             # SQL schema, database indexes, and analytical view
├── create_summary_tables.py     # Populates and indexes pre-aggregated OLAP summary tables
├── app.py                       # Main Streamlit dashboard web application
├── analysis_queries.sql         # Raw SQL scripts for the capstone's required EDA/KPIs
├── run_analysis.py              # Runner to execute analytical SQL queries
├── analysis_results.md          # Generated outputs of all analytical queries
├── final_report.md              # In-depth capstone analytical project report
├── presentation.md              # Markdown slide deck for stakeholders
├── .gitignore                   # Excludes raw large datasets and database binaries
└── LICENSE                      # MIT Open Source License
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Clone the Repository & Install Dependencies
```bash
git clone https://github.com/yourusername/us-airline-performance.git
cd us-airline-performance
pip install pandas plotly streamlit jinja2
```

### 3. Add the Raw Dataset
Download the standard **2015 Flight Delays and Cancellations** dataset from Kaggle (or BTS) and place the following three files in the root folder of the project:
*   `flights.csv` (contains main flight transaction logs, ~592MB)
*   `airports.csv` (contains airport names and locations)
*   `airlines.csv` (contains IATA airline codes and names)

---

## 🛢️ Running the Data Pipeline

Execute the following steps sequentially in your terminal to build, clean, and optimize the database:

### Step 1: Ingest Data
Ingest the raw CSV files into SQLite:
```bash
python ingest.py
```

### Step 2: Map October Airport Codes
Download the BTS lookup file and resolve October's numeric DOT identifiers:
```bash
python download_and_map_airports.py
```

### Step 3: Clean & Index Database
Set up core tables, view projections, and database indexes:
```bash
python -c "import sqlite3; conn = sqlite3.connect('airline_performance.db'); conn.executescript(open('prepare_data.sql').read()); conn.close(); print('Database schema and view created!')"
```

### Step 4: Pre-compute Aggregates (OLAP summary tables)
Materialize and index the pre-aggregated summary tables to ensure the dashboard loads instantly:
```bash
python create_summary_tables.py
```

---

## 📊 Running the Dashboard

Launch the interactive dashboard:
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser to explore the dashboard.

---

## 📝 Key Findings

*   **Cancellations:** Weather is responsible for **54.35%** of all cancellations, followed by Carrier Operations (**28.11%**).
*   **Delays:** **Late Aircraft Delay** is the largest driver of delay minutes (**39.84%**), representing a massive cascading network effect.
*   **Airline Benchmarking:** Hawaiian, Alaska, and Delta are the top performing carriers for On-Time Performance (OTP). Spirit and Frontier lag behind, while American Eagle (MQ) has an extremely high cancellation rate of **5.10%**.
*   **Airport Bottlenecks:** LaGuardia (LGA) and Chicago O'Hare (ORD) are the worst performing major hubs. Salt Lake City (SLC) is the most efficient major airport with **86.86% OTP**.
*   **Temporal Peaks:** Saturdays are the most reliable days to fly. Departing between **5:00 AM and 7:00 AM** yields a >90% OTP, whereas delays peak between **6:00 PM and 8:00 PM** due to accumulated schedule drag.

---

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
