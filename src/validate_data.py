
import pandas as pd
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

file_path = base_path / "data" / "processed" / "metropt3_cleaned.csv"

total_rows = 0
duplicate_indices = 0
invalid_timestamps = 0
out_of_order = 0

previous_timestamp = None
seen_indices = set()

sensor_columns = [
    "TP2", "TP3", "H1", "DV_pressure",
    "Reservoirs", "Oil_temperature", "Motor_current",
    "COMP", "DV_eletric", "Towers", "MPG",
    "LPS", "Pressure_switch", "Oil_level",
    "Caudal_impulses"
]

sensor_min = {col: float("inf") for col in sensor_columns}
sensor_max = {col: float("-inf") for col in sensor_columns}

sensor_unique = {col: set() for col in [
    "COMP", "DV_eletric", "Towers", "MPG",
    "LPS", "Pressure_switch", "Oil_level",
    "Caudal_impulses"
]}

for chunk in pd.read_csv(file_path, chunksize=100000):

    total_rows += len(chunk)

    # Check duplicate record indices
    for value in chunk["record_index"]:
        if value in seen_indices:
            duplicate_indices += 1
        seen_indices.add(value)

    # Validate timestamps
    timestamps = pd.to_datetime(chunk["timestamp"], errors="coerce")

    invalid_timestamps += timestamps.isna().sum()

    if not timestamps.is_monotonic_increasing:
        out_of_order += 1

    if previous_timestamp is not None:
        if timestamps.iloc[0] < previous_timestamp:
            out_of_order += 1

    previous_timestamp = timestamps.iloc[-1]

    # Calculate sensor ranges
    for col in sensor_columns:
        sensor_min[col] = min(sensor_min[col], chunk[col].min())
        sensor_max[col] = max(sensor_max[col], chunk[col].max())

    # Collect unique digital sensor values
    for col in sensor_unique:
        sensor_unique[col].update(chunk[col].dropna().unique())

print("\n========== VALIDATION REPORT ==========")

print("Total records:", total_rows)
print("Duplicate record indices:", duplicate_indices)
print("Invalid timestamps:", invalid_timestamps)
print("Out-of-order chunks:", out_of_order)

print("\n========== SENSOR RANGES ==========")

for col in sensor_columns:
    print(f"{col}: Min={sensor_min[col]}, Max={sensor_max[col]}")

print("\n========== UNIQUE DIGITAL VALUES ==========")

for col, values in sensor_unique.items():
    print(f"{col}: {sorted(values)}")

print("\n========== CONSTANT SENSOR CHECK ==========")

for col, values in sensor_unique.items():
    if len(values) == 1:
        print(f"{col} is constant: {values}")

print("\nVALIDATION COMPLETED!")
