
import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTTP_FILE = ROOT / "data" / "http_metrics.csv"
DNS_FILE = ROOT / "data" / "dns_metrics.csv"


def load_records(path):
    records = []

    if not path.is_file():
        print(f"Missing metrics file: {path}")
        return records

    with path.open(newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            try:
                timestamp = datetime.fromisoformat(
                    row["timestamp_utc"]
                )

                if timestamp.tzinfo is None:
                    continue

                status = row["status"].strip().upper()
                if status not in ("UP", "DOWN"):
                    continue

                records.append({
                    "time": timestamp.astimezone(timezone.utc),
                    "status": status
                })

            except (ValueError, KeyError, TypeError):
                continue

    return sorted(records, key=lambda r: r["time"])


def failure_windows(records):
    windows = []
    start = None

    for record in records:
        if record["status"] == "DOWN":
            if start is None:
                start = record["time"]

        elif start is not None:
            windows.append((start, record["time"]))
            start = None

    if start is not None:
        windows.append((start, None))

    return windows


def overlap(a, b):
    start_a, end_a = a
    start_b, end_b = b

    max_time = datetime.max.replace(tzinfo=timezone.utc)

    return (
        start_a <= (end_b or max_time)
        and start_b <= (end_a or max_time)
    )


def analyze():
    http = load_records(HTTP_FILE)
    dns = load_records(DNS_FILE)

    print("Enterprise Observability - Correlation Analysis")
    print("-" * 50)
    print(f"HTTP records: {len(http)}")
    print(f"DNS records: {len(dns)}")

    if not http or not dns:
        print("Insufficient data for cross-signal analysis.")
        return

    http_failures = failure_windows(http)
    dns_failures = failure_windows(dns)

    print(f"HTTP failure windows: {len(http_failures)}")
    print(f"DNS failure windows: {len(dns_failures)}")

    matched_http = set()
    matched_dns = set()

    for i, h in enumerate(http_failures):
        for j, d in enumerate(dns_failures):
            if overlap(h, d):
                matched_http.add(i)
                matched_dns.add(j)

                print("\nOVERLAPPING FAILURES")
                print(f"HTTP window: {h}")
                print(f"DNS window:  {d}")
                print(
                    "Hypothesis: shared dependency or "
                    "independent simultaneous failures."
                )

    for i, window in enumerate(http_failures):
        if i not in matched_http:
            print("\nHTTP-ONLY FAILURE")
            print(f"Window: {window}")
            print(
                "Hypothesis: application, server, "
                "or HTTP-specific path."
            )

    for j, window in enumerate(dns_failures):
        if j not in matched_dns:
            print("\nDNS-ONLY FAILURE")
            print(f"Window: {window}")
            print(
                "Hypothesis: resolver or DNS-specific path."
            )

    if not http_failures and not dns_failures:
        print("\nNo recorded failures in either signal.")


if __name__ == "__main__":
    analyze()
