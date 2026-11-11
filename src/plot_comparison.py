
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

input_file = base_path / "reports" / "load_matched_comparison.csv"
output_file = base_path / "reports" / "load_matched_comparison.png"

df = pd.read_csv(input_file)

# Sensors to compare
sensors = [
    "TP2",
    "TP3",
    "H1",
    "Reservoirs",
    "Oil_temperature",
    "Motor_current"
]

# Exclude record counts
df = df.set_index("failure_event")

ax = df[sensors].T.plot(
    kind="bar",
    figsize=(14, 7),
    width=0.8
)

ax.set_title("Sensor Comparison During Loaded Operation")
ax.set_xlabel("Sensor")
ax.set_ylabel("Average Sensor Reading")
ax.legend(title="Operating Period")

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig(output_file, dpi=150)
plt.close()

print("Comparison chart saved:", output_file)
print("VISUALIZATION COMPLETED!")
