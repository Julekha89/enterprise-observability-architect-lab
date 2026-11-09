import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from incidents.correlation_engine import failure_windows, overlap


def record(timestamp, status):
    return {
        "time": datetime.fromisoformat(timestamp),
        "status": status,
    }


class CorrelationEngineTests(unittest.TestCase):

    def test_no_failures(self):
        records = [
            record("2026-11-09T10:00:00+00:00", "UP"),
            record("2026-11-09T10:01:00+00:00", "UP"),
        ]
        self.assertEqual(failure_windows(records), [])

    def test_failure_and_recovery(self):
        records = [
            record("2026-11-09T10:00:00+00:00", "DOWN"),
            record("2026-11-09T10:01:00+00:00", "DOWN"),
            record("2026-11-09T10:02:00+00:00", "UP"),
        ]
        windows = failure_windows(records)
        self.assertEqual(len(windows), 1)
        self.assertEqual(
            windows[0][1],
            datetime(2026, 11, 9, 10, 2, tzinfo=timezone.utc),
        )

    def test_open_failure_window(self):
        records = [
            record("2026-11-09T10:00:00+00:00", "DOWN"),
        ]
        windows = failure_windows(records)
        self.assertEqual(len(windows), 1)
        self.assertIsNone(windows[0][1])

    def test_overlapping_failures(self):
        http = (
            datetime.fromisoformat("2026-11-09T10:00:00+00:00"),
            datetime.fromisoformat("2026-11-09T10:05:00+00:00"),
        )
        dns = (
            datetime.fromisoformat("2026-11-09T10:03:00+00:00"),
            datetime.fromisoformat("2026-11-09T10:07:00+00:00"),
        )
        self.assertTrue(overlap(http, dns))

    def test_non_overlapping_failures(self):
        http = (
            datetime.fromisoformat("2026-11-09T10:00:00+00:00"),
            datetime.fromisoformat("2026-11-09T10:02:00+00:00"),
        )
        dns = (
            datetime.fromisoformat("2026-11-09T10:05:00+00:00"),
            datetime.fromisoformat("2026-11-09T10:07:00+00:00"),
        )
        self.assertFalse(overlap(http, dns))


if __name__ == "__main__":
    unittest.main()
