import csv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "data" / "http_metrics.csv"
THRESHOLD = 3

def analyze():
    if not METRICS.exists():
        print("Metrics file not found.")
        return

    with METRICS.open(newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    failures = 0
    incident = None
    incidents = []
    first_failure = None

    for row in rows:
        status = row["status"].strip().upper()
        timestamp = row["timestamp_utc"]

        if status == "DOWN":
            failures += 1
            if failures == 1:
                first_failure = timestamp

            if failures == THRESHOLD and incident is None:
                incident = {
                    "first_failure": first_failure,
                    "opened_at": timestamp,
                    "recovered_at": None,
                    "severity": "CRITICAL",
                    "status": "OPEN"
                }
                incidents.append(incident)

        elif status == "UP":
            failures = 0
            first_failure = None

            if incident is not None:
                incident["recovered_at"] = timestamp
                incident["status"] = "RECOVERED"
                incident = None

    print(f"Monitoring records analyzed: {len(rows)}")
    print(f"Confirmed incidents: {len(incidents)}")

    for index, item in enumerate(incidents, start=1):
        print(f"\nINCIDENT-{index:03d}")
        for key, value in item.items():
            print(f"  {key}: {value}")

        if item["recovered_at"]:
            start = datetime.fromisoformat(item["first_failure"])
            end = datetime.fromisoformat(item["recovered_at"])
            duration = (end - start).total_seconds()
            print(f"  observed_failure_window_seconds: {duration:.2f}")

if __name__ == "__main__":
    analyze()
