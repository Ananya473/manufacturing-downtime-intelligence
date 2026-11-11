
import os
import numpy as np
import pandas as pd

# --------------------------------------------------
# 1. SETTINGS
# --------------------------------------------------

INPUT_FILE = "data/processed/metropt3_labeled.csv"
OUTPUT_DIR = "reports"

FEATURES = [
    "TP2",
    "TP3",
    "Reservoirs",
    "Oil_temperature",
    "Motor_current"
]

EVENT_COLUMN = "failure_event"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------
# 2. LOAD SAMPLES
# --------------------------------------------------

print("Reading dataset...")

normal_samples = []
event_samples = []

for chunk in pd.read_csv(INPUT_FILE, chunksize=100000):

    normal = chunk[chunk[EVENT_COLUMN] == "Normal"]
    events = chunk[chunk[EVENT_COLUMN] != "Normal"]

    if not normal.empty:
        normal_samples.append(
            normal.sample(
                n=min(len(normal), 5000),
                random_state=42
            )[FEATURES]
        )

    if not events.empty:
        event_samples.append(
            events.sample(
                n=min(len(events), 2000),
                random_state=42
            )[FEATURES + [EVENT_COLUMN]]
        )

normal_data = pd.concat(normal_samples, ignore_index=True)
event_data = pd.concat(event_samples, ignore_index=True)

normal_data = normal_data.replace(
    [np.inf, -np.inf], np.nan
).dropna()

event_data = event_data.replace(
    [np.inf, -np.inf], np.nan
).dropna()

print("Normal samples:", len(normal_data))
print("Event samples:", len(event_data))

# --------------------------------------------------
# 3. SPLIT NORMAL DATA
# --------------------------------------------------

normal_data = normal_data.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

n = len(normal_data)

normal_train = normal_data.iloc[:int(n * 0.60)].copy()
normal_calibration = normal_data.iloc[
    int(n * 0.60):int(n * 0.80)
].copy()

# --------------------------------------------------
# 4. CALCULATE SENSOR STATISTICS
# --------------------------------------------------

median = normal_train.median()

mad = (
    normal_train.sub(median)
    .abs()
    .median()
)

iqr = (
    normal_train.quantile(0.75)
    - normal_train.quantile(0.25)
)

std = normal_train.std()

scale = mad * 1.4826

scale = scale.where(scale > 0.000001, iqr / 1.349)
scale = scale.where(scale > 0.000001, std)
scale = scale.clip(lower=0.000001)

# --------------------------------------------------
# 5. COMPARE NORMAL AND EVENT DISTRIBUTIONS
# --------------------------------------------------

rows = []

for feature in FEATURES:

    normal_values = normal_train[feature]
    event_values = event_data[feature]

    normal_q99 = normal_values.quantile(0.99)
    normal_q01 = normal_values.quantile(0.01)

    rows.append({
        "sensor": feature,
        "normal_median": normal_values.median(),
        "normal_MAD": mad[feature],
        "normal_IQR": iqr[feature],
        "normal_std": std[feature],
        "calculated_scale": scale[feature],
        "normal_1st_percentile": normal_q01,
        "normal_99th_percentile": normal_q99,
        "normal_max": normal_values.max(),
        "event_median": event_values.median(),
        "event_1st_percentile": event_values.quantile(0.01),
        "event_99th_percentile": event_values.quantile(0.99),
        "event_max": event_values.max(),
        "event_above_normal_99th_pct": (
            event_values > normal_q99
        ).mean() * 100
    })

comparison = pd.DataFrame(rows)

print("\n========== SENSOR DISTRIBUTION COMPARISON ==========")
print(comparison.round(4).to_string(index=False))

comparison.to_csv(
    os.path.join(OUTPUT_DIR, "sensor_diagnostic_comparison.csv"),
    index=False
)

# --------------------------------------------------
# 6. CHECK WHICH SENSOR CREATES THE HIGH SCORE
# --------------------------------------------------

normal_deviations = (
    normal_calibration.sub(median)
    .abs()
    .div(scale)
)

event_deviations = (
    event_data[FEATURES].sub(median)
    .abs()
    .div(scale)
)

print("\n========== NORMAL CALIBRATION DEVIATIONS ==========")

print(
    normal_deviations.describe(
        percentiles=[0.90, 0.95, 0.99, 0.995]
    ).round(2).to_string()
)

print("\n========== EVENT DEVIATIONS ==========")

print(
    event_deviations.describe(
        percentiles=[0.50, 0.90, 0.95, 0.99]
    ).round(2).to_string()
)

# --------------------------------------------------
# 7. FIND THE SENSOR WITH THE LARGEST DEVIATION
# --------------------------------------------------

normal_max_sensor = normal_deviations.idxmax(axis=1)
event_max_sensor = event_deviations.idxmax(axis=1)

print("\n========== LARGEST DEVIATION BY SENSOR ==========")

print("\nNormal calibration:")
print(normal_max_sensor.value_counts().to_string())

print("\nDocumented event windows:")
print(event_max_sensor.value_counts().to_string())

# --------------------------------------------------
# 8. EVENT-WISE SENSOR COMPARISON
# --------------------------------------------------

event_comparison = (
    event_data.groupby(EVENT_COLUMN)[FEATURES]
    .median()
    .round(4)
)

print("\n========== MEDIAN SENSOR VALUES BY EVENT ==========")
print(event_comparison.to_string())

event_comparison.to_csv(
    os.path.join(OUTPUT_DIR, "event_sensor_medians.csv")
)

# --------------------------------------------------
# 9. SAVE DIAGNOSTIC REPORT
# --------------------------------------------------

print("\nDiagnostic files saved:")
print("reports/sensor_diagnostic_comparison.csv")
print("reports/event_sensor_medians.csv")

print("\nDiagnostic analysis completed.")
