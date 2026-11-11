
import pandas as pd
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

input_file = (
    base_path / "data" / "processed" / "metropt3_labeled.csv"
)

output_file = (
    base_path / "reports" / "load_matched_comparison.csv"
)

sensors = [
    "TP2",
    "TP3",
    "H1",
    "Reservoirs",
    "Oil_temperature",
    "Motor_current"
]

columns = ["failure_event", "DV_eletric"] + sensors

# Store totals and counts
totals = {}
counts = {}

for chunk in pd.read_csv(
    input_file,
    usecols=columns,
    chunksize=100000
):

    # Keep only records where compressor is working under load
    chunk = chunk[chunk["DV_eletric"] == 1]

    grouped = chunk.groupby("failure_event")[sensors].agg(
        ["sum", "count"]
    )

    for event in grouped.index:

        if event not in totals:
            totals[event] = {col: 0.0 for col in sensors}
            counts[event] = 0

        counts[event] += int(
            grouped.loc[event, (sensors[0], "count")]
        )

        for sensor in sensors:
            totals[event][sensor] += grouped.loc[
                event, (sensor, "sum")
            ]

# Calculate averages
results = []

for event, values in totals.items():

    row = {
        "failure_event": event,
        "record_count": counts[event]
    }

    for sensor in sensors:
        row[sensor] = values[sensor] / counts[event]

    results.append(row)

summary = pd.DataFrame(results)

summary = summary.sort_values("failure_event")

summary.to_csv(output_file, index=False)

print("\n========== LOAD-MATCHED ANALYSIS ==========")
print(summary.round(4).to_string(index=False))

print("\nSaved report:", output_file)
print("\nLOAD-MATCHED ANALYSIS COMPLETED!")
