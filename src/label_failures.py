
import pandas as pd
from pathlib import Path

base_path = Path(__file__).resolve().parents[1]

input_file = base_path / "data" / "processed" / "metropt3_cleaned.csv"
output_file = base_path / "data" / "processed" / "metropt3_labeled.csv"

# Documented failure periods from UCI
failure_events = [
    {
        "event": "Air_Leak_1",
        "start": "2020-04-18 00:00:00",
        "end": "2020-04-18 23:59:00"
    },
    {
        "event": "Air_Leak_2",
        "start": "2020-05-29 23:30:00",
        "end": "2020-05-30 06:00:00"
    },
    {
        "event": "Air_Leak_3",
        "start": "2020-06-05 10:00:00",
        "end": "2020-06-07 14:30:00"
    },
    {
        "event": "Air_Leak_4",
        "start": "2020-07-15 14:30:00",
        "end": "2020-07-15 19:00:00"
    }
]

events = [
    (
        event["event"],
        pd.Timestamp(event["start"]),
        pd.Timestamp(event["end"])
    )
    for event in failure_events
]

total_rows = 0
failure_counts = {event[0]: 0 for event in events}

for chunk_number, chunk in enumerate(
    pd.read_csv(input_file, chunksize=100000)
):

    chunk["timestamp"] = pd.to_datetime(chunk["timestamp"])

    # Default: outside documented failure periods
    chunk["failure_event"] = "Normal"

    # Assign documented failure labels
    for event_name, start, end in events:

        mask = chunk["timestamp"].between(start, end)

        chunk.loc[mask, "failure_event"] = event_name

        failure_counts[event_name] += int(mask.sum())

    # Binary reference label
    chunk["is_failure_period"] = (
        chunk["failure_event"] != "Normal"
    ).astype(int)

    # Save labelled data
    chunk.to_csv(
        output_file,
        mode="w" if chunk_number == 0 else "a",
        header=(chunk_number == 0),
        index=False
    )

    total_rows += len(chunk)

    print(f"Labelled {total_rows:,} records")

print("\n========== FAILURE LABEL SUMMARY ==========")

for event_name, count in failure_counts.items():
    print(f"{event_name}: {count:,} records")

total_failure_records = sum(failure_counts.values())

print("\nTotal records:", total_rows)
print("Documented failure-period records:", total_failure_records)
print("Outside failure periods:", total_rows - total_failure_records)

print("\nSaved labelled dataset:", output_file)
print("\nFAILURE LABELLING COMPLETED!")
