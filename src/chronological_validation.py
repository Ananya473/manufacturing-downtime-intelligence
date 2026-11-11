
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
TIMESTAMP = "timestamp"

CUTOFF_DATE = pd.Timestamp("2020-06-01")

SENSORS = [
    "TP3",
    "Reservoirs",
    "Oil_temperature"
]

CHUNK_SIZE = 100000
SAMPLE_SIZE = 5000

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("CHRONOLOGICAL VALIDATION")
print("=" * 60)

print("\nReference period: Before", CUTOFF_DATE.date())
print("Validation period: From", CUTOFF_DATE.date())

# ==================================================
# 2. BUILD REFERENCE DATA FROM THE PAST
# ==================================================

print("\nStep 1: Building historical normal reference...")

normal_samples = []
training_records = 0

for chunk in pd.read_csv(
    INPUT_FILE,
    chunksize=CHUNK_SIZE
):

    chunk[TIMESTAMP] = pd.to_datetime(
        chunk[TIMESTAMP],
        errors="coerce"
    )

    historical_normal = chunk[
        (chunk[TIMESTAMP] < CUTOFF_DATE) &
        (chunk[EVENT] == "Normal") &
        (chunk[STATE] == 1)
    ]

    training_records += len(historical_normal)

    if not historical_normal.empty:

        sample = historical_normal[SENSORS].sample(
            n=min(len(historical_normal), SAMPLE_SIZE),
            random_state=42
        )

        normal_samples.append(sample)

if not normal_samples:
    raise ValueError(
        "No historical normal reference records found."
    )

reference = pd.concat(
    normal_samples,
    ignore_index=True
)

reference = reference.replace(
    [np.inf, -np.inf], np.nan
).dropna()

print("Historical normal records:", training_records)
print("Reference sample records:", len(reference))

# ==================================================
# 3. CALCULATE THRESHOLDS USING PAST DATA ONLY
# ==================================================

print("\nStep 2: Calculating historical thresholds...")

thresholds = {
    "TP3": reference["TP3"].quantile(0.10),
    "Reservoirs": reference["Reservoirs"].quantile(0.10),
    "Oil_temperature": reference["Oil_temperature"].quantile(0.90)
}

for sensor, value in thresholds.items():
    print(f"{sensor}: {value:.4f}")

threshold_table = pd.DataFrame([
    {
        "sensor": sensor,
        "threshold": value,
        "rule": (
            "Below 10th percentile"
            if sensor in ["TP3", "Reservoirs"]
            else "Above 90th percentile"
        )
    }
    for sensor, value in thresholds.items()
])

threshold_table.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "chronological_validation_thresholds.csv"
    ),
    index=False
)

# ==================================================
# 4. PREPARE VALIDATION OUTPUT
# ==================================================

print("\nStep 3: Evaluating future records...")

alert_file = os.path.join(
    OUTPUT_DIR,
    "chronological_validation_alerts.csv"
)

if os.path.exists(alert_file):
    os.remove(alert_file)

summary_data = {}

validation_records = 0
validation_start = None
validation_end = None

# ==================================================
# 5. PROCESS FUTURE DATA ONLY
# ==================================================

for chunk in pd.read_csv(
    INPUT_FILE,
    chunksize=CHUNK_SIZE
):

    chunk[TIMESTAMP] = pd.to_datetime(
        chunk[TIMESTAMP],
        errors="coerce"
    )

    future_data = chunk[
        (chunk[TIMESTAMP] >= CUTOFF_DATE) &
        (chunk[STATE] == 1)
    ].copy()

    if future_data.empty:
        continue

    validation_records += len(future_data)

    chunk_start = future_data[TIMESTAMP].min()
    chunk_end = future_data[TIMESTAMP].max()

    if validation_start is None:
        validation_start = chunk_start
        validation_end = chunk_end
    else:
        validation_start = min(validation_start, chunk_start)
        validation_end = max(validation_end, chunk_end)

    # --------------------------------------------------
    # PRESSURE SIGNAL
    # --------------------------------------------------

    future_data["pressure_signal"] = (
        (future_data["TP3"] < thresholds["TP3"]) &
        (future_data["Reservoirs"] < thresholds["Reservoirs"])
    )

    # --------------------------------------------------
    # TEMPERATURE SIGNAL
    # --------------------------------------------------

    future_data["temperature_signal"] = (
        future_data["Oil_temperature"] >
        thresholds["Oil_temperature"]
    )

    # --------------------------------------------------
    # COMBINED INVESTIGATION ALERT
    # --------------------------------------------------

    future_data["investigation_alert"] = (
        future_data["pressure_signal"] &
        future_data["temperature_signal"]
    )

    # --------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------

    future_data["alert_reason"] = "No alert"

    future_data.loc[
        future_data["pressure_signal"],
        "alert_reason"
    ] = "Low pressure signal"

    future_data.loc[
        future_data["temperature_signal"],
        "alert_reason"
    ] = "High temperature signal"

    future_data.loc[
        future_data["pressure_signal"] &
        future_data["temperature_signal"],
        "alert_reason"
    ] = "Low pressure + high temperature"

    # --------------------------------------------------
    # SAVE FUTURE ALERT RECORDS
    # --------------------------------------------------

    alerts = future_data[
        future_data["investigation_alert"]
    ].copy()

    if not alerts.empty:

        alerts[[
            TIMESTAMP,
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
    # AGGREGATE VALIDATION RESULTS
    # --------------------------------------------------

    grouped = future_data.groupby(EVENT).agg(
        total_records=("investigation_alert", "count"),
        pressure_signals=("pressure_signal", "sum"),
        temperature_signals=("temperature_signal", "sum"),
        alerts=("investigation_alert", "sum")
    )

    for event, row in grouped.iterrows():

        if event not in summary_data:
            summary_data[event] = {
                "total_records": 0,
                "pressure_signals": 0,
                "temperature_signals": 0,
                "alerts": 0
            }

        for column in summary_data[event]:
            summary_data[event][column] += int(row[column])

# ==================================================
# 6. CREATE FINAL VALIDATION SUMMARY
# ==================================================

print("\nStep 4: Preparing validation summary...")

rows = []

for event, values in summary_data.items():

    records = values["total_records"]

    rows.append({
        "failure_event": event,
        "total_records": records,
        "pressure_signals": values["pressure_signals"],
        "temperature_signals": values["temperature_signals"],
        "combined_alerts": values["alerts"],
        "alert_rate_percent": (
            values["alerts"] / records * 100
            if records else 0
        )
    })

summary = pd.DataFrame(rows)

summary = summary.sort_values(
    "failure_event"
)

summary.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "chronological_validation_summary.csv"
    ),
    index=False
)

# ==================================================
# 7. DISPLAY RESULTS
# ==================================================

print("\n" + "=" * 60)
print("CHRONOLOGICAL VALIDATION RESULTS")
print("=" * 60)

print("\nValidation period:")
print("Start:", validation_start)
print("End:", validation_end)

print("\nValidation records:", validation_records)

print("\nEvent-wise results:")

print(
    summary.round(3).to_string(index=False)
)

print("\n" + "=" * 60)
print("FILES GENERATED")
print("=" * 60)

print("reports/chronological_validation_thresholds.csv")
print("reports/chronological_validation_summary.csv")
print("reports/chronological_validation_alerts.csv")

print("\nChronological validation completed.")
