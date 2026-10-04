import csv
import sqlite3

# Define paths
db_path = "/Users/jackb/Desktop/linkedin-leads/cyprus_leads.db"
csv_output_path = "/Users/jackb/Desktop/linkedin-leads/espocrm_import.csv"

# Connect to SQLite database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Fetch all leads from the database
cursor.execute("SELECT * FROM leads")
rows = cursor.fetchall()

if rows:
    # Get column names dynamically
    fieldnames = rows[0].keys()

    # Write data to CSV
    with open(csv_output_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    print(f"Successfully exported {len(rows)} records to: {csv_output_path}")
else:
    print("No records found in the leads table.")

conn.close()