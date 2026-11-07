import csv
import socket
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT / "data" / "dns_metrics.csv"

DOMAIN = "example.com"
INTERVAL = 30

def check_dns():
    start = time.perf_counter()

    try:
        results = socket.getaddrinfo(
            DOMAIN,
            None,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM
        )

        addresses = sorted({
            item[4][0] for item in results
        })

        latency = round(
            (time.perf_counter() - start) * 1000, 2
        )

        return "UP", latency, ";".join(addresses), ""

    except (socket.gaierror, OSError) as error:
        latency = round(
            (time.perf_counter() - start) * 1000, 2
        )

        return "DOWN", latency, "", str(error)


def main():
    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    new_file = (
        not LOG_FILE.exists()
        or LOG_FILE.stat().st_size == 0
    )

    with LOG_FILE.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if new_file:
            writer.writerow([
                "timestamp_utc",
                "domain",
                "status",
                "resolution_ms",
                "ip_addresses",
                "error"
            ])
            file.flush()

        print(
            "DNS monitoring started. "
            "Press Ctrl+C to stop.",
            flush=True
        )

        try:
            while True:
                timestamp = datetime.now(
                    timezone.utc
                ).isoformat()

                status, latency, ips, error = check_dns()

                writer.writerow([
                    timestamp,
                    DOMAIN,
                    status,
                    latency,
                    ips,
                    error
                ])

                file.flush()

                print(
                    f"{timestamp} | {DOMAIN} | "
                    f"{status} | {latency} ms | "
                    f"{ips} | {error}",
                    flush=True
                )

                time.sleep(INTERVAL)

        except KeyboardInterrupt:
            print("\nDNS monitoring stopped.")


if __name__ == "__main__":
    main()
