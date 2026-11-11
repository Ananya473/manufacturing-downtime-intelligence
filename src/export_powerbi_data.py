
import sqlite3
import pandas as pd
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

db_file = base_path / "data" / "processed" / "manufacturing.db"

output_folder = base_path / "powerbi" / "data"
output_folder.mkdir(parents=True, exist_ok=True)

connection = sqlite3.connect(db_file)

# ==========================================
# 1. FAILURE SUMMARY
# ==========================================

failure_query = """
SELECT
    failure_event,
    COUNT(*) AS total_records,

    ROUND(AVG(TP2), 3) AS avg_TP2,
    ROUND(AVG(TP3), 3) AS avg_TP3,
    ROUND(AVG(H1), 3) AS avg_H1,
    ROUND(AVG(Reservoirs), 3) AS avg_reservoirs,
    ROUND(AVG(Oil_temperature), 3) AS avg_oil_temperature,
    ROUND(AVG(Motor_current), 3) AS avg_motor_current,

    SUM(CASE WHEN DV_eletric = 1 THEN 1 ELSE 0 END)
        AS loaded_records

FROM sensor_readings

GROUP BY failure_event
"""

failure_summary = pd.read_sql_query(
    failure_query, connection
)

failure_summary.to_csv(
    output_folder / "failure_summary.csv",
    index=False
)

print("Exported failure summary")


# ==========================================
# 2. OPERATING STATE SUMMARY
# ==========================================

operating_query = """
SELECT
    failure_event,
    COUNT(*) AS total_records,

    ROUND(AVG(COMP) * 100, 2) AS COMP_percentage,
    ROUND(AVG(DV_eletric) * 100, 2) AS DV_eletric_percentage,
    ROUND(AVG(Towers) * 100, 2) AS Towers_percentage,
    ROUND(AVG(MPG) * 100, 2) AS MPG_percentage,
    ROUND(AVG(LPS) * 100, 2) AS LPS_percentage

FROM sensor_readings

GROUP BY failure_event
"""

operating_summary = pd.read_sql_query(
    operating_query, connection
)

operating_summary.to_csv(
    output_folder / "operating_summary.csv",
    index=False
)

print("Exported operating summary")


# ==========================================
# 3. TEN-MINUTE SENSOR TRENDS
# ==========================================

trend_query = """
SELECT
    strftime('%Y-%m-%d %H:', timestamp) ||
    printf(
        '%02d',
        (CAST(strftime('%M', timestamp) AS INTEGER) / 10) * 10
    ) || ':00' AS time_bucket,

    failure_event,

    COUNT(*) AS record_count,

    ROUND(AVG(TP2), 4) AS TP2,
    ROUND(AVG(TP3), 4) AS TP3,
    ROUND(AVG(H1), 4) AS H1,
    ROUND(AVG(Reservoirs), 4) AS Reservoirs,
    ROUND(AVG(Oil_temperature), 4) AS Oil_temperature,
    ROUND(AVG(Motor_current), 4) AS Motor_current,

    ROUND(AVG(DV_eletric) * 100, 2)
        AS loaded_percentage

FROM sensor_readings

GROUP BY time_bucket, failure_event

ORDER BY time_bucket
"""

sensor_trends = pd.read_sql_query(
    trend_query, connection
)

sensor_trends.to_csv(
    output_folder / "sensor_trends.csv",
    index=False
)

print("Exported sensor trends")


# ==========================================
# 4. ANOMALY DETECTION SUMMARY
# ==========================================

anomaly_file = (
    base_path / "reports" / "anomaly_detection_results.csv"
)

anomaly_data = pd.read_csv(anomaly_file)

anomaly_summary = (
    anomaly_data
    .groupby(["failure_event", "is_anomaly"])
    .size()
    .reset_index(name="record_count")
)

anomaly_summary.to_csv(
    output_folder / "anomaly_summary.csv",
    index=False
)

print("Exported anomaly summary")


# ==========================================
# 5. EXPORT SUMMARY
# ==========================================

connection.close()

print("\n========== POWER BI EXPORT SUMMARY ==========")

for file in output_folder.glob("*.csv"):
    print(f"{file.name}: {file.stat().st_size / 1024:.2f} KB")

print("\nAll Power BI datasets exported successfully!")
