import sqlite3
import pandas as pd
import re

db_name = "airline_performance.db"
sql_file = "analysis_queries.sql"
output_file = "analysis_results.md"

print("Connecting to database...")
conn = sqlite3.connect(db_name)

# Read the SQL file
with open(sql_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Split SQL content into separate queries.
# We'll split on semicolon but ignore semicolons inside comments or strings.
# A simple regex split on semicolon followed by newline is usually sufficient.
queries = re.split(r';\s*\n', sql_content)

markdown_out = "# SQL Analytical Query Results\n\n"
markdown_out += "This file contains the output tables of the analytical queries executed on `airline_performance.db`.\n\n"

query_names = [
    "1. Overall Flight Volumes, Cancellations, and Diversions",
    "2. Cancellations by Reason",
    "3. Delay Statistics (Departure & Arrival)",
    "4. Distribution of Delay Types",
    "5. KPI Aggregation by Airline",
    "6. KPI Aggregation by Origin Airport (Top 20 by Volume)",
    "7. KPI Aggregation by Month",
    "8. Day of Week Analysis",
    "9. Scheduled Departure Hour Analysis"
]

print("Executing queries...")
for i, query in enumerate(queries):
    query = query.strip()
    if not query:
        continue
    
    name = query_names[i] if i < len(query_names) else f"Query {i+1}"
    print(f"Running: {name}...")
    
    markdown_out += f"## {name}\n\n"
    markdown_out += "```sql\n" + query + "\n```\n\n### Results:\n\n"
    
    try:
        # Run query using pandas
        df = pd.read_sql_query(query, conn)
        # Convert to markdown table
        markdown_out += df.to_markdown(index=False) + "\n\n"
    except Exception as e:
        print(f"Error running query {name}: {e}")
        markdown_out += f"**ERROR EXECUTE:** {e}\n\n"

# Write results to file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(markdown_out)

conn.close()
print(f"Analysis complete! Results saved to {output_file}.")
