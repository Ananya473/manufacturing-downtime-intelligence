
import pandas as pd
from pathlib import Path

# 1. Locate the dataset
file_path = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "MetroPT3(AirCompressor).csv"
)

# 2. Load the first 10,000 records
df = pd.read_csv(file_path, nrows=10000)

# 3. Display dataset dimensions
print("\n========== DATASET SHAPE ==========")
print(df.shape)

# 4. Display column names
print("\n========== COLUMN NAMES ==========")
print(df.columns.tolist())

# 5. Display first five records
print("\n========== FIRST FIVE ROWS ==========")
print(df.head())

# 6. Check missing values
print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

# 7. Check data types
print("\n========== DATA TYPES ==========")
print(df.dtypes)

# 8. Statistical summary
print("\n========== STATISTICAL SUMMARY ==========")
print(df.describe())

print("\n========== INSPECTION COMPLETED ==========")

print("\n========== COMPLETE FIRST FIVE ROWS ==========")
print(df.head().to_string())

print("\n========== TIMESTAMP INFORMATION ==========")
print("First timestamp:", df["timestamp"].iloc[0])
print("Last timestamp:", df["timestamp"].iloc[-1])

print("\n========== UNIQUE SENSOR VALUES ==========")

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

for col in digital_columns:
    print(f"\n{col}:")
    print(df[col].value_counts().head(10))
