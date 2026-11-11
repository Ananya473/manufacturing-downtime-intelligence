
import pandas as pd
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

input_file = base_path / "data" / "processed" / "metropt3_labeled.csv"
output_file = base_path / "reports" / "sensor_comparison.csv"

# Sensors selected for analysis
sensors = [
    "TP2",
    "TP3",
    "H1",
    "DV_pressure",
    "Reservoirs",
    "Oil_temperature",
    "Motor_current"
]

columns = ["failure_event"] + sensors

# Store totals for every event
sensor_sums = {}
record_counts = {}

# Process complete dataset in chunks
for chunk in pd.read_csv(input_file, usecols=columns, chunksize=100000):

    grouped = chunk.groupby("failure_event")[sensors].agg(
        ["sum", "count"]
    )

    for event in grouped.index:

        if event not in sensor_sums:
            sensor_sums[event] = {
                sensor: 0.0 for sensor in sensors
            }
            record_counts[event] = 0

        record_counts[event] += int(
            grouped.loc[event, (sensors[0], "count")]
        )

        for sensor in sensors:
            sensor_sums[event][sensor] += grouped.loc[
                event, (sensor, "sum")
            ]

    print("Processed another 100,000 records...")

# Calculate average sensor values
results = []

for event, values in sensor_sums.items():

    row = {
        "failure_event": event,
        "record_count": record_counts[event]
    }

    for sensor in sensors:
        row[sensor] = (
            values[sensor] / record_counts[event]
        )

    results.append(row)

summary = pd.DataFrame(results)

# Put normal operation first
summary["sort_order"] = summary["failure_event"].apply(
    lambda x: 0 if x == "Normal" else 1
)

summary = (
    summary.sort_values(["sort_order", "failure_event"])
    .drop(columns="sort_order")
)

# Save results
summary.to_csv(output_file, index=False)

print("\n========== SENSOR COMPARISON ==========")
print(summary.round(4).to_string(index=False))

print("\nSaved report:", output_file)
print("\nFAILURE ANALYSIS COMPLETED!")
