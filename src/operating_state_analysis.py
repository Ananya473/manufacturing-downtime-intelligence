
import pandas as pd
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

input_file = (
    base_path / "data" / "processed" / "metropt3_labeled.csv"
)

output_file = (
    base_path / "reports" / "operating_state_comparison.csv"
)

digital_columns = [
    "COMP",
    "DV_eletric",
    "Towers",
    "MPG",
    "LPS",
    "Pressure_switch",
    "Oil_level",
    "Caudal_impulses"
]

columns = ["failure_event"] + digital_columns

# Store sums and counts
state_sums = {}
state_counts = {}

for chunk in pd.read_csv(
    input_file,
    usecols=columns,
    chunksize=100000
):

    grouped = chunk.groupby("failure_event")[digital_columns].agg(
        ["sum", "count"]
    )

    for event in grouped.index:

        if event not in state_sums:
            state_sums[event] = {
                col: 0 for col in digital_columns
            }
            state_counts[event] = 0

        state_counts[event] += int(
            grouped.loc[event, (digital_columns[0], "count")]
        )

        for col in digital_columns:
            state_sums[event][col] += grouped.loc[
                event, (col, "sum")
            ]

# Calculate percentages
results = []

for event, values in state_sums.items():

    row = {
        "failure_event": event,
        "record_count": state_counts[event]
    }

    for col in digital_columns:
        row[col + "_percent_1"] = (
            values[col] / state_counts[event]
        ) * 100

    results.append(row)

summary = pd.DataFrame(results)

summary.to_csv(output_file, index=False)

print("\n========== OPERATING STATE COMPARISON ==========")
print(summary.round(2).to_string(index=False))

print("\nReport saved:", output_file)
print("\nOPERATING STATE ANALYSIS COMPLETED!")
