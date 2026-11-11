
import os
import pandas as pd
import numpy as np

# ==================================================
# 1. SETTINGS
# ==================================================

INPUT_FILE = "data/processed/metropt3_labeled.csv"
OUTPUT_DIR = "reports"

EVENT = "failure_event"
STATE = "DV_eletric"

SENSORS = [
    "TP3",
    "Reservoirs",
    "Oil_temperature"
]

CHUNK_SIZE = 100000
SAMPLE_SIZE = 5000

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 55)
print("IMPROVED SENSOR INVESTIGATION")
print("=" * 55)

# ==================================================
# 2. BUILD NORMAL REFERENCE
# ==================================================

print("\nStep 1: Building normal reference...")

normal_samples = []

for chunk in pd.read_csv(INPUT_FILE, chunksize=CHUNK_SIZE):

    normal = chunk[
        (chunk[EVENT] == "Normal") &
        (chunk[STATE] == 1)
    ]

    if not normal.empty:
        normal_samples.append(
            normal[SENSORS].sample(
                n=min(len(normal), SAMPLE_SIZE),
                random_state=42
            )
        )

reference = pd.concat(
    normal_samples,
    ignore_index=True
)

reference = reference.replace(
    [np.inf, -np.inf], np.nan
).dropna()

# ==================================================
# 3. CALCULATE THRESHOLDS
# ==================================================

thresholds = {
    "TP3": reference["TP3"].quantile(0.10),
    "Reservoirs": reference["Reservoirs"].quantile(0.10),
    "Oil_temperature": reference["Oil_temperature"].quantile(0.90)
}

print("\nCalculated thresholds:")

for sensor, value in thresholds.items():
    print(f"{sensor}: {value:.4f}")

pd.DataFrame([
    {
        "sensor": sensor,
        "threshold": value
    }
    for sensor, value in thresholds.items()
]).to_csv(
    os.path.join(OUTPUT_DIR, "sensor_rule_thresholds.csv"),
    index=False
)

# ==================================================
# 4. PREPARE OUTPUT FILES
# ==================================================

alert_file = os.path.join(
    OUTPUT_DIR,
    "sensor_investigation_alerts.csv"
)

if os.path.exists(alert_file):
    os.remove(alert_file)

summary_data = {}

total_records = 0
total_matched_records = 0
total_alerts = 0

# ==================================================
# 5. PROCESS DATASET
# ==================================================

print("\nStep 2: Investigating sensor readings...")

for chunk in pd.read_csv(INPUT_FILE, chunksize=CHUNK_SIZE):

    total_records += len(chunk)

    data = chunk[
        chunk[STATE] == 1
    ].copy()

    if data.empty:
        continue

    total_matched_records += len(data)

    # --------------------------------------------------
    # PRESSURE SIGNAL
    # Both pressure sensors must be below threshold.
    # --------------------------------------------------

    data["pressure_signal"] = (
        (data["TP3"] < thresholds["TP3"]) &
        (data["Reservoirs"] < thresholds["Reservoirs"])
    )

    # --------------------------------------------------
    # TEMPERATURE SIGNAL
    # --------------------------------------------------

    data["temperature_signal"] = (
        data["Oil_temperature"] >
        thresholds["Oil_temperature"]
    )

    # --------------------------------------------------
    # COMBINED ALERT
    # Both independent signal groups must be present.
    # --------------------------------------------------

    data["investigation_alert"] = (
        data["pressure_signal"] &
        data["temperature_signal"]
    )

    # --------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------

    data["alert_reason"] = "No alert"

    data.loc[
        data["pressure_signal"],
        "alert_reason"
    ] = "Low pressure signal"

    data.loc[
        data["temperature_signal"],
        "alert_reason"
    ] = "High temperature signal"

    data.loc[
        data["pressure_signal"] &
        data["temperature_signal"],
        "alert_reason"
    ] = "Low pressure + high temperature"

    # --------------------------------------------------
    # SAVE ALERT RECORDS
    # --------------------------------------------------

    alerts = data[data["investigation_alert"]].copy()

    if not alerts.empty:

        alerts[[
            "timestamp",
            EVENT,
            STATE,
            "TP3",
            "Reservoirs",
            "Oil_temperature",
            "pressure_signal",
            "temperature_signal",
            "investigation_alert",
            "alert_reason"
        ]].to_csv(
            alert_file,
            mode="a",
            header=not os.path.exists(alert_file),
            index=False
        )

    # --------------------------------------------------
    # EVENT-WISE AGGREGATION
    # --------------------------------------------------

    grouped = data.groupby(EVENT).agg(
        records=("investigation_alert", "count"),
        pressure_signals=("pressure_signal", "sum"),
        temperature_signals=("temperature_signal", "sum"),
        alerts=("investigation_alert", "sum")
    )

    for event, row in grouped.iterrows():

        if event not in summary_data:
            summary_data[event] = {
                "records": 0,
                "pressure_signals": 0,
                "temperature_signals": 0,
                "alerts": 0
            }

        for column in summary_data[event]:
            summary_data[event][column] += int(row[column])

    total_alerts += int(
        data["investigation_alert"].sum()
    )

    if total_records % 500000 < CHUNK_SIZE:
        print(f"Processed {total_records:,} records...")

# ==================================================
# 6. CREATE FINAL SUMMARY
# ==================================================

rows = []

for event, values in summary_data.items():

    records = values["records"]

    rows.append({
        "failure_event": event,
        "total_records": records,
        "pressure_signal_records": values["pressure_signals"],
        "temperature_signal_records": values["temperature_signals"],
        "combined_alerts": values["alerts"],
        "alert_rate_percent": (
            values["alerts"] / records * 100
            if records else 0
        )
    })

summary = pd.DataFrame(rows)

summary.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "sensor_investigation_summary.csv"
    ),
    index=False
)

# ==================================================
# 7. DISPLAY RESULTS
# ==================================================

print("\n========== IMPROVED INVESTIGATION RESULTS ==========")

print(summary.round(3).to_string(index=False))

print("\nTotal dataset records:", total_records)
print("Matched operating-state records:", total_matched_records)
print("Combined investigation alerts:", total_alerts)

print("\n========== GENERATED FILES ==========")

print("reports/sensor_rule_thresholds.csv")
print("reports/sensor_investigation_summary.csv")
print("reports/sensor_investigation_alerts.csv")

print("\nInvestigation completed successfully.")
