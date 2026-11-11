
import os
import pandas as pd

# --------------------------------------------------
# 1. SETTINGS
# --------------------------------------------------

INPUT_FILE = "data/processed/metropt3_labeled.csv"
OUTPUT_DIR = "reports"

EVENT_COLUMN = "failure_event"
STATE_COLUMN = "DV_eletric"

SENSORS = [
    "TP2",
    "TP3",
    "Reservoirs",
    "Oil_temperature",
    "Motor_current"
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------
# 2. PROCESS THE COMPLETE DATASET
# --------------------------------------------------

print("Starting operating-state-matched analysis...")

all_results = []
total_rows = 0

for chunk in pd.read_csv(INPUT_FILE, chunksize=100000):

    total_rows += len(chunk)

    grouped = (
        chunk.groupby(
            [EVENT_COLUMN, STATE_COLUMN]
        )[SENSORS]
        .agg(["sum", "count"])
    )

    all_results.append(grouped)

    if total_rows % 500000 < 100000:
        print(f"Processed {total_rows:,} records...")

print(f"\nTotal records processed: {total_rows:,}")

# --------------------------------------------------
# 3. COMBINE RESULTS FROM ALL CHUNKS
# --------------------------------------------------

combined = pd.concat(all_results)

# Sum sensor totals and counts across chunks.
combined = combined.groupby(level=[0, 1]).sum()

# --------------------------------------------------
# 4. CALCULATE FINAL SENSOR AVERAGES
# --------------------------------------------------

rows = []

for (event, state), values in combined.iterrows():

    row = {
        "failure_event": event,
        "DV_eletric": state
    }

    for sensor in SENSORS:

        count = values[(sensor, "count")]
        total = values[(sensor, "sum")]

        row[sensor + "_mean"] = (
            total / count if count else None
        )

        row[sensor + "_count"] = int(count)

    rows.append(row)

summary = pd.DataFrame(rows)

summary = summary.sort_values(
    ["DV_eletric", "failure_event"]
)

# --------------------------------------------------
# 5. COMPARE EACH EVENT AGAINST NORMAL
# WITH THE SAME OPERATING STATE
# --------------------------------------------------

comparison_rows = []

normal_rows = summary[
    summary["failure_event"] == "Normal"
]

for _, event_row in summary[
    summary["failure_event"] != "Normal"
].iterrows():

    matching_normal = normal_rows[
        normal_rows["DV_eletric"] == event_row["DV_eletric"]
    ]

    if matching_normal.empty:
        continue

    normal_row = matching_normal.iloc[0]

    for sensor in SENSORS:

        normal_value = normal_row[sensor + "_mean"]
        event_value = event_row[sensor + "_mean"]

        difference = event_value - normal_value

        percentage_difference = (
            (difference / abs(normal_value)) * 100
            if normal_value != 0 else None
        )

        comparison_rows.append({
            "failure_event": event_row["failure_event"],
            "DV_eletric": event_row["DV_eletric"],
            "sensor": sensor,
            "normal_mean": normal_value,
            "event_mean": event_value,
            "absolute_difference": difference,
            "percentage_difference": percentage_difference,
            "event_records": event_row[sensor + "_count"],
            "normal_records": normal_row[sensor + "_count"]
        })

comparison = pd.DataFrame(comparison_rows)

# --------------------------------------------------
# 6. SAVE RESULTS
# --------------------------------------------------

summary.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "state_matched_sensor_summary.csv"
    ),
    index=False
)

comparison.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "state_matched_sensor_comparison.csv"
    ),
    index=False
)

# --------------------------------------------------
# 7. DISPLAY RESULTS
# --------------------------------------------------

print("\n========== FINAL SENSOR AVERAGES ==========")

print(
    summary.round(4).to_string(index=False)
)

print("\n========== EVENT VS NORMAL COMPARISON ==========")

print(
    comparison.round(4).to_string(index=False)
)

print("\n========== OUTPUT FILES ==========")

print("reports/state_matched_sensor_summary.csv")
print("reports/state_matched_sensor_comparison.csv")

print("\nState-matched analysis completed.")

