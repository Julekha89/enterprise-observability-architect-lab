import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from probes import http_monitor


class HttpMonitorTests(unittest.TestCase):

    def mock_response(self, status, body):
        response = MagicMock()
        response.status = status
        response.read.return_value = body
        return response

    @patch.object(http_monitor, "urlopen")
    def test_healthy_response(self, mock_urlopen):
        response = self.mock_response(200, b'{"status":"healthy"}')
        mock_urlopen.return_value.__enter__.return_value = response

        status, latency, error = http_monitor.check_health()

        self.assertEqual(status, "UP")
        self.assertGreaterEqual(latency, 0)
        self.assertEqual(error, "")

    @patch.object(http_monitor, "urlopen")
    def test_unhealthy_response(self, mock_urlopen):
        response = self.mock_response(200, b'{"status":"unhealthy"}')
        mock_urlopen.return_value.__enter__.return_value = response

        status, latency, error = http_monitor.check_health()

        self.assertEqual(status, "DOWN")
        self.assertEqual(error, "")

    @patch.object(http_monitor, "urlopen")
    def test_http_500_response(self, mock_urlopen):
        response = self.mock_response(500, b'{"status":"healthy"}')
        mock_urlopen.return_value.__enter__.return_value = response

        status, latency, error = http_monitor.check_health()

        self.assertEqual(status, "DOWN")
        self.assertEqual(error, "")

    @patch.object(http_monitor, "urlopen")
    def test_connection_failure(self, mock_urlopen):
        mock_urlopen.side_effect = ConnectionRefusedError(
            "Synthetic connection failure"
        )

        status, latency, error = http_monitor.check_health()

        self.assertEqual(status, "DOWN")
        self.assertIn("Synthetic connection failure", error)


if __name__ == "__main__":
    unittest.main()
