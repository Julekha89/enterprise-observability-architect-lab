import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

URL = "http://127.0.0.1:8765/health"
INTERVAL = 30
LOG_FILE = Path(__file__).resolve().parent.parent / "data" / "http_metrics.csv"

def check_health():
    start = time.perf_counter()
    try:
        with urlopen(URL, timeout=5) as response:
            body = json.load(response)
            latency = round((time.perf_counter() - start) * 1000, 2)
            healthy = (
                response.status == 200
                and body.get("status") == "healthy"
            )
            return "UP" if healthy else "DOWN", latency, ""
    except Exception as error:
        latency = round((time.perf_counter() - start) * 1000, 2)
        return "DOWN", latency, str(error)

def main():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    new_file = not LOG_FILE.exists()

    with LOG_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if new_file:
            writer.writerow(["timestamp_utc", "status", "latency_ms", "error"])
            file.flush()

        print("HTTP monitoring started. Press Ctrl+C to stop.", flush=True)
        try:
            while True:
                timestamp = datetime.now(timezone.utc).isoformat()
                status, latency, error = check_health()
                writer.writerow([timestamp, status, latency, error])
                file.flush()
                print(f"{timestamp} | {status} | {latency} ms | {error}", flush=True)
                time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
