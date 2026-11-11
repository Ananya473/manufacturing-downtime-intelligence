
import pandas as pd
import sqlite3
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

csv_file = (
    base_path / "data" / "processed" / "metropt3_labeled.csv"
)

db_file = (
    base_path / "data" / "processed" / "manufacturing.db"
)

print("Creating manufacturing database...")

connection = sqlite3.connect(db_file)

total_records = 0
first_chunk = True

# Import CSV in manageable chunks
for chunk in pd.read_csv(csv_file, chunksize=50000):

    chunk.to_sql(
        "sensor_readings",
        connection,
        if_exists="replace" if first_chunk else "append",
        index=False,
        chunksize=5000
    )

    first_chunk = False
    total_records += len(chunk)

    print(f"Imported {total_records:,} records")

# Create indexes to improve query performance
cursor = connection.cursor()

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_timestamp
ON sensor_readings(timestamp)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_failure_event
ON sensor_readings(failure_event)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_operating_state
ON sensor_readings(DV_eletric)
""")

connection.commit()

# Verify database
result = cursor.execute(
    "SELECT COUNT(*) FROM sensor_readings"
).fetchone()

print("\n========== DATABASE SUMMARY ==========")
print("Records imported:", total_records)
print("Records in database:", result[0])
print("Database location:", db_file)

connection.close()

print("\nDATABASE CREATION COMPLETED!")
