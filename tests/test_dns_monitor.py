import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from probes import dns_monitor


class DnsMonitorTests(unittest.TestCase):

    @patch.object(dns_monitor.socket, "getaddrinfo")
    def test_successful_resolution(self, mock_dns):
        mock_dns.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "",
             ("93.184.215.14", 0))
        ]

        status, latency, ips, error = dns_monitor.check_dns()

        self.assertEqual(status, "UP")
        self.assertGreaterEqual(latency, 0)
        self.assertEqual(ips, "93.184.215.14")
        self.assertEqual(error, "")

    @patch.object(dns_monitor.socket, "getaddrinfo")
    def test_multiple_ip_addresses(self, mock_dns):
        mock_dns.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "",
             ("192.0.2.2", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "",
             ("192.0.2.1", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "",
             ("192.0.2.1", 0)),
        ]

        status, latency, ips, error = dns_monitor.check_dns()

        self.assertEqual(status, "UP")
        self.assertEqual(ips, "192.0.2.1;192.0.2.2")

    @patch.object(dns_monitor.socket, "getaddrinfo")
    def test_dns_resolution_failure(self, mock_dns):
        mock_dns.side_effect = socket.gaierror(
            "Synthetic DNS failure"
        )

        status, latency, ips, error = dns_monitor.check_dns()

        self.assertEqual(status, "DOWN")
        self.assertEqual(ips, "")
        self.assertIn("Synthetic DNS failure", error)

    @patch.object(dns_monitor.socket, "getaddrinfo")
    def test_network_error(self, mock_dns):
        mock_dns.side_effect = OSError(
            "Synthetic network error"
        )

        status, latency, ips, error = dns_monitor.check_dns()

        self.assertEqual(status, "DOWN")
        self.assertIn("Synthetic network error", error)


if __name__ == "__main__":
    unittest.main()
