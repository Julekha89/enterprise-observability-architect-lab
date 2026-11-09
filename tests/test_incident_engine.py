import contextlib
import csv
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from incidents import incident_engine


class IncidentEngineTests(unittest.TestCase):

    def run_analysis(self, statuses):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic_http.csv"

            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp_utc", "status", "latency_ms", "error"])

                for index, status in enumerate(statuses):
                    writer.writerow([
                        f"2026-11-09T10:{index:02d}:00+00:00",
                        status,
                        10,
                        "",
                    ])

            output = io.StringIO()

            with patch.object(incident_engine, "METRICS", path):
                with contextlib.redirect_stdout(output):
                    incident_engine.analyze()

            return output.getvalue()

    def test_no_incidents(self):
        result = self.run_analysis(["UP", "UP", "UP"])
        self.assertIn("Confirmed incidents: 0", result)

    def test_two_failures_do_not_open_incident(self):
        result = self.run_analysis(["DOWN", "DOWN", "UP"])
        self.assertIn("Confirmed incidents: 0", result)

    def test_three_failures_open_incident(self):
        result = self.run_analysis(["DOWN", "DOWN", "DOWN"])
        self.assertIn("Confirmed incidents: 1", result)
        self.assertIn("status: OPEN", result)

    def test_incident_recovery(self):
        result = self.run_analysis(["DOWN", "DOWN", "DOWN", "UP"])
        self.assertIn("status: RECOVERED", result)
        self.assertIn("observed_failure_window_seconds:", result)

    def test_multiple_incidents(self):
        result = self.run_analysis([
            "DOWN", "DOWN", "DOWN", "UP",
            "DOWN", "DOWN", "DOWN", "UP",
        ])
        self.assertIn("Confirmed incidents: 2", result)


if __name__ == "__main__":
    unittest.main()
