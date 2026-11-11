
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

df = pd.read_csv(
    base_path / "reports" / "load_matched_comparison.csv"
)

df = df.set_index("failure_event")

# Pressure-related sensors
pressure_sensors = ["TP2", "TP3", "H1", "Reservoirs"]

df[pressure_sensors].plot(
    kind="bar",
    figsize=(12, 6)
)

plt.title("Pressure Sensor Comparison")
plt.xlabel("Operating Period")
plt.ylabel("Average Reading")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    base_path / "reports" / "pressure_comparison.png",
    dpi=150
)
plt.close()

# Temperature and electrical current
other_sensors = ["Oil_temperature", "Motor_current"]

df[other_sensors].plot(
    kind="bar",
    figsize=(12, 6)
)

plt.title("Temperature and Motor Current Comparison")
plt.xlabel("Operating Period")
plt.ylabel("Average Reading")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    base_path / "reports" / "temperature_current_comparison.png",
    dpi=150
)
plt.close()

print("Both improved charts saved successfully!")
