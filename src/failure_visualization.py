
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

input_file = base_path / "data" / "processed" / "metropt3_labeled.csv"
output_folder = base_path / "reports"

# Air Leak 3 documented period
failure_start = pd.Timestamp("2020-06-05 10:00:00")
failure_end = pd.Timestamp("2020-06-07 14:30:00")

# Include 24 hours before and after
analysis_start = failure_start - pd.Timedelta(hours=24)
analysis_end = failure_end + pd.Timedelta(hours=24)

# Sensors to visualize
sensors = [
    "TP2",
    "H1",
    "Oil_temperature",
    "Motor_current",
    "Reservoirs"
]

columns = ["timestamp"] + sensors

# Read only the required time period
selected_chunks = []

for chunk in pd.read_csv(
    input_file,
    usecols=columns,
    chunksize=100000
):

    chunk["timestamp"] = pd.to_datetime(chunk["timestamp"])

    mask = chunk["timestamp"].between(
        analysis_start,
        analysis_end
    )

    selected_chunks.append(chunk.loc[mask])

df = pd.concat(selected_chunks, ignore_index=True)

df = df.sort_values("timestamp")
df = df.set_index("timestamp")

# Aggregate into 10-minute averages
# This makes the charts easier to read
df = df.resample("10min").mean()

# Create one chart for each sensor
for sensor in sensors:

    plt.figure(figsize=(13, 5))

    plt.plot(
        df.index,
        df[sensor],
        label=sensor,
        linewidth=1
    )

    # Highlight documented failure period
    plt.axvspan(
        failure_start,
        failure_end,
        alpha=0.2,
        color="red",
        label="Documented Air Leak 3 period"
    )

    plt.title(f"{sensor} Behaviour Around Air Leak 3")
    plt.xlabel("Timestamp")
    plt.ylabel(sensor)
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()

    output_file = output_folder / f"{sensor}_air_leak_3.png"

    plt.savefig(output_file, dpi=150)
    plt.close()

    print("Chart saved:", output_file)

print("\nVISUALIZATION COMPLETED!")
