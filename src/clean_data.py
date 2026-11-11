
import pandas as pd
from pathlib import Path

# File locations
base_path = Path(__file__).resolve().parents[1]

input_file = base_path / "data" / "raw" / "MetroPT3(AirCompressor).csv"
output_file = base_path / "data" / "processed" / "metropt3_cleaned.csv"

# Cleaning summary
total_rows = 0
missing_values = None
invalid_timestamps = 0

# Read data in chunks
for chunk_number, chunk in enumerate(
    pd.read_csv(input_file, chunksize=100000)
):

    # Rename original index column
    chunk = chunk.rename(
    columns={"Unnamed: 0": "record_index"}
)

    # Convert timestamp into datetime
    chunk["timestamp"] = pd.to_datetime(
        chunk["timestamp"],
        errors="coerce"
    )

    # Count invalid timestamps
    invalid_timestamps += chunk["timestamp"].isna().sum()

    # Count missing values
    if missing_values is None:
        missing_values = chunk.isnull().sum()
    else:
        missing_values += chunk.isnull().sum()

    # Save cleaned chunk
    chunk.to_csv(
        output_file,
        mode="w" if chunk_number == 0 else "a",
        header=(chunk_number == 0),
        index=False
    )

    total_rows += len(chunk)

    print(f"Processed {total_rows:,} records")

# Final report
print("\n========== CLEANING SUMMARY ==========")
print("Total records:", total_rows)
print("Invalid timestamps:", invalid_timestamps)
print("\nMissing values:")
print(missing_values)

print("\nCleaned dataset saved at:")
print(output_file)

print("\nDATA CLEANING COMPLETED!")
