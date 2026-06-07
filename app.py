import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page config
st.set_page_config(
    page_title="U.S. Airline Performance & Delay Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    /* Gradient header banner */
    .banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #0d9488 100%);
        padding: 24px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .banner h1 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
    }
    .banner p {
        font-size: 1.1rem;
        margin: 5px 0 0 0;
        opacity: 0.9;
    }
    /* Metric container styling */
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-color: #cbd5e1;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 5px;
    }
    /* Dark mode overrides for metrics */
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background: #1e293b;
            border-color: #334155;
        }
        .metric-card:hover {
            border-color: #475569;
        }
        .metric-value {
            color: #f1f5f9;
        }
        .metric-label {
            color: #94a3b8;
        }
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = "airline_summary.db" if os.path.exists("airline_summary.db") else "airline_performance.db"

@st.cache_resource
def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Helper function to query database
def run_query(query, params=None):
    conn = get_db_connection()
    if params:
        return pd.read_sql_query(query, conn, params=params)
    return pd.read_sql_query(query, conn)

# Load basic lookup data for filters
@st.cache_data
def load_filter_data():
    airlines = run_query("SELECT IATA_CODE, AIRLINE FROM airlines ORDER BY AIRLINE")
    # Get distinct states
    states = run_query("SELECT DISTINCT STATE FROM airports WHERE STATE IS NOT NULL ORDER BY STATE")
    return airlines, states

# Header
st.markdown("""
<div class="banner">
    <h1>✈️ U.S. Airline Performance & Delay Analytics</h1>
    <p>Interactive dashboard analyzing 5.8 million domestic flights to identify operational bottlenecks and KPIs</p>
</div>
""", unsafe_allow_html=True)

# Check database existence
if not os.path.exists(DB_PATH):
    st.error(f"Database file '{DB_PATH}' not found. Please run the ingestion and data preparation scripts first.")
    st.stop()

# Load filters
airlines_df, states_df = load_filter_data()

# Sidebar
st.sidebar.image("https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=300&auto=format&fit=crop&q=80")
st.sidebar.title("Dashboard Controls")

# Multi-select filters
selected_airlines = st.sidebar.multiselect(
    "Filter by Airlines",
    options=airlines_df["IATA_CODE"].tolist(),
    format_func=lambda x: f"{x} - {airlines_df[airlines_df['IATA_CODE'] == x]['AIRLINE'].values[0]}"
)

selected_months = st.sidebar.multiselect(
    "Filter by Month",
    options=list(range(1, 13)),
    format_func=lambda x: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][x-1]
)

# Navigation
page = st.sidebar.radio(
    "Navigate to:",
    ["Overview Dashboard", "Airline Performance", "Airport Analysis", "Temporal Trends", "SQL Playground"]
)

# Build dynamic filter clause
def get_filters():
    clauses = []
    params = []
    if selected_airlines:
        clauses.append("f.AIRLINE_CODE IN (" + ",".join(["?"] * len(selected_airlines)) + ")")
        params.extend(selected_airlines)
    if selected_months:
        clauses.append("f.MONTH IN (" + ",".join(["?"] * len(selected_months)) + ")")
        params.extend(selected_months)
    
    where_clause = " WHERE " + " AND ".join(clauses) if clauses else ""
    return where_clause, params

where_clause, params = get_filters()

# ----------------- PAGE 1: OVERVIEW DASHBOARD -----------------
if page == "Overview Dashboard":
    st.subheader("📊 Operational Performance Overview")
    
    # Query summary tables (runs in < 1ms)
    kpi_query = f"""
        SELECT
            SUM(f.total_flights) AS total_flights,
            SUM(f.cancelled_flights) AS total_cancelled,
            SUM(f.diverted_flights) AS total_diverted,
            ROUND(1.0 * SUM(f.total_dep_delay) / SUM(f.total_flights - f.cancelled_flights), 2) AS avg_dep_delay,
            ROUND(1.0 * SUM(f.total_arr_delay) / SUM(f.total_flights - f.cancelled_flights - f.diverted_flights), 2) AS avg_arr_delay,
            SUM(f.on_time_arrivals) AS on_time
        FROM agg_airline_monthly f
        {where_clause}
    """
    
    with st.spinner("Calculating overall KPIs..."):
        kpi_data = run_query(kpi_query, params).iloc[0]
        
    total_flights = kpi_data['total_flights'] or 0
    total_cancelled = kpi_data['total_cancelled'] or 0
    total_diverted = kpi_data['total_diverted'] or 0
    avg_dep_delay = kpi_data['avg_dep_delay'] or 0.0
    avg_arr_delay = kpi_data['avg_arr_delay'] or 0.0
    on_time = kpi_data['on_time'] or 0
    
    cancellation_rate = (total_cancelled / total_flights * 100) if total_flights > 0 else 0.0
    otp_rate = (on_time / (total_flights - total_cancelled - total_diverted) * 100) if (total_flights - total_cancelled - total_diverted) > 0 else 0.0
    
    # Render KPI Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_flights:,.0f}</div>
                <div class="metric-label">Total Flights</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{otp_rate:.2f}%</div>
                <div class="metric-label">On-Time Performance (OTP)</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{cancellation_rate:.2f}%</div>
                <div class="metric-label">Cancellation Rate</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_dep_delay:.2f} m</div>
                <div class="metric-label">Avg Departure Delay</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sub-layouts for graphs
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.markdown("### 🚫 Cancellations by Reason")
        cancel_query = f"""
            SELECT
                f.Reason AS Reason,
                SUM(f.Count) AS Count
            FROM agg_cancellations_monthly f
            {where_clause}
            GROUP BY Reason
        """
        cancel_df = run_query(cancel_query, params)
        if not cancel_df.empty:
            fig_cancel = px.pie(
                cancel_df, 
                values='Count', 
                names='Reason', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_cancel.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=350)
            st.plotly_chart(fig_cancel, width="stretch")
        else:
            st.info("No cancellations recorded for current filters.")
            
    with g_col2:
        st.markdown("### ⏱️ Contribution of Delay Types")
        delay_type_query = f"""
            SELECT
                SUM(f.Airline) AS Airline,
                SUM(f.Weather) AS Weather,
                SUM(f.[National Air System (NAS)]) AS [National Air System (NAS)],
                SUM(f.Security) AS Security,
                SUM(f.[Late Aircraft]) AS [Late Aircraft]
            FROM agg_delay_types_monthly f
            {where_clause}
        """
        delay_df = run_query(delay_type_query, params)
        if not delay_df.empty and delay_df.iloc[0].sum() > 0:
            delay_series = delay_df.iloc[0]
            delay_types_df = pd.DataFrame({
                'Delay Type': delay_series.index,
                'Minutes': delay_series.values
            }).sort_values('Minutes', ascending=False)
            
            fig_delay = px.bar(
                delay_types_df,
                x='Minutes',
                y='Delay Type',
                orientation='h',
                color='Delay Type',
                text='Minutes',
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_delay.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_delay.update_layout(
                margin=dict(t=10, b=10, l=10, r=10), 
                height=350,
                showlegend=False,
                xaxis_title="Total Delayed Minutes"
            )
            st.plotly_chart(fig_delay, width="stretch")
        else:
            st.info("No delay breakdown recorded (requires delays >= 15 mins).")

# ----------------- PAGE 2: AIRLINE PERFORMANCE -----------------
elif page == "Airline Performance":
    st.subheader("✈️ Airline Performance Benchmarking")
    
    # Query summary tables (runs in < 1ms)
    airline_query = f"""
        SELECT
            f.AIRLINE_CODE AS Code,
            f.AIRLINE_NAME AS Airline,
            SUM(f.total_flights) AS Flights,
            ROUND(100.0 * SUM(f.cancelled_flights) / SUM(f.total_flights), 2) AS [Cancellation Rate (%)],
            ROUND(1.0 * SUM(f.total_dep_delay) / SUM(f.total_flights - f.cancelled_flights), 2) AS [Avg Departure Delay (min)],
            ROUND(1.0 * SUM(f.total_arr_delay) / SUM(f.total_flights - f.cancelled_flights - f.diverted_flights), 2) AS [Avg Arrival Delay (min)],
            ROUND(100.0 * SUM(f.on_time_arrivals) / SUM(f.total_flights - f.cancelled_flights - f.diverted_flights), 2) AS [OTP (%)],
            ROUND(100.0 * SUM(f.on_time_departures) / SUM(f.total_flights - f.cancelled_flights), 2) AS [Departure OTP (%)]
        FROM agg_airline_monthly f
        {where_clause}
        GROUP BY f.AIRLINE_CODE, f.AIRLINE_NAME
        ORDER BY [OTP (%)] DESC
    """
    
    with st.spinner("Aggregating airline data..."):
        airline_perf_df = run_query(airline_query, params)
        
    st.dataframe(airline_perf_df, width="stretch", hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏆 On-Time Performance (OTP) by Airline")
        fig_otp = px.bar(
            airline_perf_df,
            x='OTP (%)',
            y='Airline',
            orientation='h',
            color='OTP (%)',
            color_continuous_scale='teal',
            text='OTP (%)'
        )
        fig_otp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_otp.update_layout(yaxis={'categoryorder':'total ascending'}, height=450)
        st.plotly_chart(fig_otp, width="stretch")
        
    with col2:
        st.markdown("### ⏳ Average Arrival Delay by Airline")
        fig_arr = px.bar(
            airline_perf_df,
            x='Avg Arrival Delay (min)',
            y='Airline',
            orientation='h',
            color='Avg Arrival Delay (min)',
            color_continuous_scale='Reds',
            text='Avg Arrival Delay (min)'
        )
        fig_arr.update_traces(texttemplate='%{text:.1f} m', textposition='outside')
        fig_arr.update_layout(yaxis={'categoryorder':'total descending'}, height=450)
        st.plotly_chart(fig_arr, width="stretch")

# ----------------- PAGE 3: AIRPORT ANALYSIS -----------------
elif page == "Airport Analysis":
    st.subheader("🏢 Airport Performance & Bottlenecks")
    
    # Query summary tables (runs in < 5ms)
    airport_query = f"""
        SELECT
            agg.Code AS Code,
            ap.AIRPORT AS Name,
            ap.CITY AS City,
            ap.STATE AS State,
            ap.LATITUDE AS Lat,
            ap.LONGITUDE AS Lon,
            agg.Flights AS Flights,
            agg.Avg_Delay AS [Avg Departure Delay (min)],
            agg.Cancel_Rate AS [Cancellation Rate (%)],
            agg.OTP AS [OTP (%)]
        FROM (
            SELECT
                f.AIRPORT_CODE AS Code,
                SUM(f.total_flights) AS Flights,
                ROUND(1.0 * SUM(f.total_dep_delay) / SUM(f.total_flights - f.cancelled_flights), 2) AS Avg_Delay,
                ROUND(100.0 * SUM(f.cancelled_flights) / SUM(f.total_flights), 2) AS Cancel_Rate,
                ROUND(100.0 * SUM(f.on_time_arrivals) / SUM(f.total_flights - f.cancelled_flights - f.diverted_flights), 2) AS OTP
            FROM agg_airport_monthly f
            {where_clause}
            GROUP BY Code
        ) agg
        LEFT JOIN airports ap ON agg.Code = ap.IATA_CODE
        ORDER BY Flights DESC
        LIMIT 50
    """
    
    with st.spinner("Aggregating airport statistics..."):
        airport_perf_df = run_query(airport_query, params)
        
    # Drop rows with missing lat/lon for mapping
    map_df = airport_perf_df.dropna(subset=['Lat', 'Lon'])
    
    # Map visualization
    st.markdown("### 🗺️ Top 50 U.S. Airports (Size = Traffic Volume, Color = On-Time Performance)")
    if not map_df.empty:
        fig_map = px.scatter_geo(
            map_df,
            lat='Lat',
            lon='Lon',
            hover_name='Name',
            hover_data=['Code', 'City', 'State', 'Flights', 'OTP (%)', 'Avg Departure Delay (min)'],
            size='Flights',
            color='OTP (%)',
            color_continuous_scale='RdYlGn', 
            projection="albers usa",
            title="Airport Traffic and OTP Map"
        )
        fig_map.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_map, width="stretch")
    else:
        st.info("Geographical coordinates missing for selected filters.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ⚠️ Most Delayed Airports (Worst Avg Departure Delay)")
        worst_delay = airport_perf_df.sort_values('Avg Departure Delay (min)', ascending=False).head(10)
        fig_worst_delay = px.bar(
            worst_delay,
            x='Avg Departure Delay (min)',
            y='Code',
            orientation='h',
            text='Avg Departure Delay (min)',
            color='Avg Departure Delay (min)',
            color_continuous_scale='Oranges',
            hover_data=['Name', 'City']
        )
        fig_worst_delay.update_traces(texttemplate='%{text:.1f} m', textposition='outside')
        fig_worst_delay.update_layout(yaxis={'categoryorder':'total ascending'}, height=350)
        st.plotly_chart(fig_worst_delay, width="stretch")
        
    with col2:
        st.markdown("### 🛑 Highest Cancellation Rates by Airport")
        worst_cancel = airport_perf_df.sort_values('Cancellation Rate (%)', ascending=False).head(10)
        fig_worst_cancel = px.bar(
            worst_cancel,
            x='Cancellation Rate (%)',
            y='Code',
            orientation='h',
            text='Cancellation Rate (%)',
            color='Cancellation Rate (%)',
            color_continuous_scale='Reds',
            hover_data=['Name', 'City']
        )
        fig_worst_cancel.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_worst_cancel.update_layout(yaxis={'categoryorder':'total ascending'}, height=350)
        st.plotly_chart(fig_worst_cancel, width="stretch")

# ----------------- PAGE 4: TEMPORAL TRENDS -----------------
elif page == "Temporal Trends":
    st.subheader("📅 Temporal Performance Trends")
    
    st.markdown("### 📈 Monthly Trends in Flight Volume and On-Time Performance")
    # Query summary tables (runs in < 1ms)
    month_query = f"""
        SELECT
            f.MONTH,
            SUM(f.total_flights) AS Flights,
            ROUND(100.0 * SUM(f.cancelled_flights) / SUM(f.total_flights), 2) AS [Cancellation Rate (%)],
            ROUND(1.0 * SUM(f.total_dep_delay) / SUM(f.total_flights - f.cancelled_flights), 2) AS [Avg Departure Delay (min)],
            ROUND(100.0 * SUM(f.on_time_arrivals) / SUM(f.total_flights - f.cancelled_flights - f.diverted_flights), 2) AS [OTP (%)]
        FROM agg_airline_monthly f
        {where_clause}
        GROUP BY f.MONTH
        ORDER BY f.MONTH
    """
    month_df = run_query(month_query, params)
    
    # Month list names
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_df['Month Name'] = month_df['MONTH'].apply(lambda x: month_names[x-1])
    
    # Double axis plot
    fig_month = go.Figure()
    fig_month.add_trace(go.Bar(
        x=month_df['Month Name'],
        y=month_df['Flights'],
        name='Flight Volume',
        yaxis='y',
        marker_color='#3b82f6',
        opacity=0.8
    ))
    fig_month.add_trace(go.Scatter(
        x=month_df['Month Name'],
        y=month_df['OTP (%)'],
        name='OTP (%)',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#0d9488', width=3),
        marker=dict(size=8)
    ))
    
    fig_month.update_layout(
        title='Monthly Volumetric and On-Time Performance',
        yaxis=dict(title='Flight Volume', side='left'),
        yaxis2=dict(title='OTP (%)', side='right', overlaying='y', range=[50, 100]),
        legend=dict(x=0.01, y=0.99),
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig_month, width="stretch")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🗓️ Day of Week Performance (Monday to Sunday)")
        # Query summary tables (runs in < 1ms)
        day_query = f"""
            SELECT
                f.DAY_OF_WEEK,
                SUM(f.total_flights) AS Flights,
                ROUND(1.0 * SUM(f.total_dep_delay) / SUM(f.total_flights - f.cancelled_flights), 2) AS [Avg Departure Delay (min)],
                ROUND(100.0 * SUM(f.on_time_arrivals) / SUM(f.total_flights - f.cancelled_flights), 2) AS [OTP (%)]
            FROM agg_temporal_daily f
            {where_clause}
            GROUP BY f.DAY_OF_WEEK
            ORDER BY f.DAY_OF_WEEK
        """
        day_df = run_query(day_query, params)
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_df['Day'] = day_df['DAY_OF_WEEK'].apply(lambda x: day_names[x-1])
        
        fig_day = px.line(
            day_df,
            x='Day',
            y='OTP (%)',
            text='OTP (%)',
            title='On-Time Performance by Day of Week',
            markers=True
        )
        fig_day.update_traces(textposition="bottom right", texttemplate='%{text:.1f}%')
        fig_day.update_layout(height=350, yaxis_range=[70, 90])
        st.plotly_chart(fig_day, width="stretch")
        
    with col2:
        st.markdown("### ⏰ Hourly Delay Patterns (By Scheduled Departure Hour)")
        # Query summary tables (runs in < 1ms)
        hour_query = f"""
            SELECT
                f.HOUR AS Hour,
                ROUND(1.0 * SUM(f.total_dep_delay) / SUM(f.total_flights), 2) AS [Avg Departure Delay (min)],
                ROUND(100.0 * SUM(f.on_time_arrivals) / SUM(f.total_flights), 2) AS [OTP (%)]
            FROM agg_temporal_hourly f
            {where_clause}
            GROUP BY Hour
            ORDER BY Hour
        """
        hour_df = run_query(hour_query, params)
        fig_hour = px.line(
            hour_df,
            x='Hour',
            y='Avg Departure Delay (min)',
            title='Average Departure Delay by Hour of Day',
            markers=True,
            color_discrete_sequence=['#ea580c']
        )
        fig_hour.update_layout(height=350, xaxis=dict(tickmode='linear', tick0=0, dtick=2))
        st.plotly_chart(fig_hour, width="stretch")

# ----------------- PAGE 5: SQL PLAYGROUND -----------------
elif page == "SQL Playground":
    st.subheader("💻 Interactive SQL Query Playground")
    st.markdown("""
        Write custom SQL queries against the `airline_performance.db` database.
        The main view is **`v_flights_analytical`**, which joins flights, airlines, and airports.
        Other tables include **`airlines`**, **`airports`**, and **`airport_mappings`**.
        
        *Example query:* `SELECT AIRLINE_NAME, COUNT(*) FROM v_flights_analytical GROUP BY AIRLINE_NAME`
    """)
    
    # Default text area content
    default_sql = "SELECT AIRLINE_NAME, COUNT(*) AS Total_Flights, ROUND(AVG(DEPARTURE_DELAY), 2) AS Avg_Delay\nFROM v_flights_analytical\nGROUP BY AIRLINE_NAME\nORDER BY Total_Flights DESC\nLIMIT 10;"
    
    query_input = st.text_area("Write SQL Query here:", value=default_sql, height=150)
    
    if st.button("Execute Query"):
        if query_input:
            with st.spinner("Executing custom SQL query..."):
                try:
                    res_df = run_query(query_input)
                    st.success("Query executed successfully!")
                    st.markdown(f"**Row Count:** {len(res_df)}")
                    st.dataframe(res_df, width="stretch")
                    
                    # Add download button
                    csv_data = res_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv_data,
                        file_name="sql_query_results.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"SQL Error: {e}")
        else:
            st.warning("Please enter a SQL query.")
