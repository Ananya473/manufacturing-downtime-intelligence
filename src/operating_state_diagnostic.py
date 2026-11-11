
import os
import pandas as pd

# --------------------------------------------------
# 1. SETTINGS
# --------------------------------------------------

INPUT_FILE = "data/processed/metropt3_labeled.csv"
OUTPUT_DIR = "reports"

EVENT = "failure_event"

STATE_COLUMNS = [
    "COMP",
    "DV_eletric",
    "Towers",
    "Pressure_switch",
    "LPS",
    "MPG"
]

SENSOR_COLUMNS = [
    "TP2",
    "TP3",
    "Reservoirs",
    "Oil_temperature",
    "Motor_current"
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------
# 2. PREPARE AGGREGATION STORAGE
# --------------------------------------------------

state_results = {column: [] for column in STATE_COLUMNS}

combination_results = []
sensor_results = []
relationship_results = []

print("Analysing the COMPLETE dataset in chunks...")

# --------------------------------------------------
# 3. PROCESS ALL RECORDS
# --------------------------------------------------

total_rows = 0

for chunk_number, chunk in enumerate(
    pd.read_csv(INPUT_FILE, chunksize=100000),
    start=1
):

    total_rows += len(chunk)

    # Event counts by individual operating state
    for column in STATE_COLUMNS:

        grouped = (
            chunk.groupby([EVENT, column], dropna=False)
            .size()
            .reset_index(name="records")
        )

        state_results[column].append(grouped)

    # Count combinations of all operating states
    combinations = (
        chunk.groupby(
            [EVENT] + STATE_COLUMNS,
            dropna=False
        )
        .size()
        .reset_index(name="records")
    )

    combination_results.append(combinations)

    # Sensor averages by event and DV_eletric state
    grouped_sensors = (
        chunk.groupby([EVENT, "DV_eletric"])[SENSOR_COLUMNS]
        .agg(["count", "sum"])
    )

    sensor_results.append(grouped_sensors)

    # Check whether COMP and MPG are identical
    relationship_results.append({
        "comp_equals_mpg": (
            chunk["COMP"] == chunk["MPG"]
        ).sum(),
        "comp_mpg_compared": len(chunk),
        "comp_equals_dv_inverse": (
            chunk["COMP"] == (1 - chunk["DV_eletric"])
        ).sum()
    })

    if chunk_number % 5 == 0:
        print(
            f"Processed {total_rows:,} records..."
        )

print(f"\nTotal records processed: {total_rows:,}")

# --------------------------------------------------
# 4. EVENT COUNTS BY INDIVIDUAL STATE
# --------------------------------------------------

print("\n========== EVENT COUNTS BY STATE ==========")

for column in STATE_COLUMNS:

    result = (
        pd.concat(state_results[column])
        .groupby([EVENT, column])["records"]
        .sum()
        .reset_index()
    )

    result.to_csv(
        os.path.join(
            OUTPUT_DIR,
            f"state_distribution_{column}.csv"
        ),
        index=False
    )

    print(f"\n--- {column} ---")
    print(result.to_string(index=False))

# --------------------------------------------------
# 5. COMBINATIONS OF OPERATING STATES
# --------------------------------------------------

all_combinations = (
    pd.concat(combination_results)
    .groupby([EVENT] + STATE_COLUMNS)["records"]
    .sum()
    .reset_index()
    .sort_values(
        ["failure_event", "records"],
        ascending=[True, False]
    )
)

all_combinations.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "operating_state_combinations.csv"
    ),
    index=False
)

print("\n========== MOST COMMON STATE COMBINATIONS ==========")

for event_name, group in all_combinations.groupby(EVENT):

    print(f"\n{event_name}")

    print(
        group.head(10).to_string(index=False)
    )

# --------------------------------------------------
# 6. SENSOR AVERAGES BY EVENT AND DV_ELETRIC
# --------------------------------------------------

combined_sensor_data = pd.concat(sensor_results)

sensor_summary = pd.DataFrame(index=combined_sensor_data.index)

for sensor in SENSOR_COLUMNS:

    counts = combined_sensor_data[
        (sensor, "count")
    ]

    sums = combined_sensor_data[
        (sensor, "sum")
    ]

    sensor_summary[sensor + "_mean"] = (
        sums / counts
    )

sensor_summary["record_count"] = (
    combined_sensor_data[
        (SENSOR_COLUMNS[0], "count")
    ]
)

sensor_summary = sensor_summary.reset_index()

sensor_summary.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "sensor_means_by_event_and_state.csv"
    ),
    index=False
)

print("\n========== SENSOR MEANS BY EVENT AND DV_ELETRIC ==========")
print(sensor_summary.round(4).to_string(index=False))

# --------------------------------------------------
# 7. CHECK RELATIONSHIPS BETWEEN STATE COLUMNS
# --------------------------------------------------

relationship_data = pd.DataFrame(relationship_results)

total_compared = relationship_data[
    "comp_mpg_compared"
].sum()

comp_equals_mpg = relationship_data[
    "comp_equals_mpg"
].sum()

comp_equals_inverse = relationship_data[
    "comp_equals_dv_inverse"
].sum()

print("\n========== STATE COLUMN RELATIONSHIPS ==========")

print(
    f"COMP equals MPG: "
    f"{comp_equals_mpg:,} / {total_compared:,} "
    f"({comp_equals_mpg / total_compared * 100:.2f}%)"
)

print(
    f"COMP equals (1 - DV_eletric): "
    f"{comp_equals_inverse:,} / {total_compared:,} "
    f"({comp_equals_inverse / total_compared * 100:.2f}%)"
)

# --------------------------------------------------
# 8. SAVE FINAL REPORT
# --------------------------------------------------

print("\n========== FILES CREATED ==========")

print("reports/state_distribution_COMP.csv")
print("reports/state_distribution_DV_eletric.csv")
print("reports/state_distribution_Towers.csv")
print("reports/state_distribution_Pressure_switch.csv")
print("reports/state_distribution_LPS.csv")
print("reports/state_distribution_MPG.csv")
print("reports/operating_state_combinations.csv")
print("reports/sensor_means_by_event_and_state.csv")

print("\nOperating state diagnostic completed.")
