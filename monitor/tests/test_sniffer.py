import os
import unittest
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone
from scapy.all import ICMP, IP, TCP, UDP, Raw
from scapy.packet import Packet as ScapyPacket

from ..models import Packet
from ..sniffer import (
    PacketCaptureConfig,
    advanced_packet_callback,
    capture_packets_on_interface,
)


class PacketCaptureConfigTestCase(TestCase):
    def setUp(self):
        # Backup original environment variables
        self.original_env = {
            "NETCREEP_CAPTURE_INTERFACES": os.environ.get(
                "NETCREEP_CAPTURE_INTERFACES"
            ),
            "NETCREEP_MAX_PACKETS": os.environ.get("NETCREEP_MAX_PACKETS"),
            "NETCREEP_PACKET_FILTER": os.environ.get("NETCREEP_PACKET_FILTER"),
            "NETCREEP_CAPTURE_TIMEOUT": os.environ.get("NETCREEP_CAPTURE_TIMEOUT"),
        }

    def tearDown(self):
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)

    def test_load_from_env_default_values(self):
        # Test default configuration loading
        os.environ["NETCREEP_CAPTURE_INTERFACES"] = "eth0,lo"
        config = PacketCaptureConfig.load_from_env()

        self.assertEqual(config.CAPTURE_INTERFACES, ["eth0", "lo"])
        self.assertEqual(config.MAX_PACKETS, None)
        self.assertEqual(config.TIMEOUT, 60)

    def test_load_from_env_custom_values(self):
        # Test custom configuration loading
        os.environ["NETCREEP_CAPTURE_INTERFACES"] = "wlan0"
        os.environ["NETCREEP_MAX_PACKETS"] = "5000"
        os.environ["NETCREEP_PACKET_FILTER"] = "tcp port 80"
        os.environ["NETCREEP_CAPTURE_TIMEOUT"] = "120"

        config = PacketCaptureConfig.load_from_env()

        self.assertEqual(config.CAPTURE_INTERFACES, ["wlan0"])
        self.assertEqual(config.MAX_PACKETS, "5000")
        self.assertEqual(config.FILTER, "tcp port 80")
        self.assertEqual(config.TIMEOUT, 120)


class PacketProcessingTestCase(TestCase):
    def setUp(self):
        # Clear existing packets before each test
        Packet.objects.all().delete()

    def _create_test_packet(
        self, protocol="TCP", src_ip="192.168.1.100", dst_ip="10.0.0.1"
    ):
        """Helper method to create test Scapy packets"""
        if protocol == "TCP":
            packet = IP(src=src_ip, dst=dst_ip) / TCP(sport=12345, dport=80)
        elif protocol == "UDP":
            packet = IP(src=src_ip, dst=dst_ip) / UDP(sport=53, dport=53)
        elif protocol == "ICMP":
            packet = IP(src=src_ip, dst=dst_ip) / ICMP()
        else:
            packet = IP(src=src_ip, dst=dst_ip) / Raw(load=b"Test Packet")
        return packet

    def test_advanced_packet_callback_tcp(self):
        # Test TCP packet processing
        test_packet = self._create_test_packet(protocol="TCP")

        with patch("django.utils.timezone.now", return_value=timezone.now()):
            advanced_packet_callback(test_packet)

        # Verify packet was saved
        saved_packet = Packet.objects.first()
        self.assertIsNotNone(saved_packet)
        self.assertEqual(saved_packet.protocol, "TCP")
        self.assertEqual(saved_packet.src_ip, "192.168.1.100")
        self.assertEqual(saved_packet.dst_ip, "10.0.0.1")
        self.assertEqual(saved_packet.src_port, 12345)
        self.assertEqual(saved_packet.dst_port, 80)

    def test_advanced_packet_callback_udp(self):
        # Test UDP packet processing
        test_packet = self._create_test_packet(protocol="UDP")

        with patch("django.utils.timezone.now", return_value=timezone.now()):
            advanced_packet_callback(test_packet)

        # Verify packet was saved
        saved_packet = Packet.objects.first()
        self.assertIsNotNone(saved_packet)
        self.assertEqual(saved_packet.protocol, "UDP")
        self.assertEqual(saved_packet.src_ip, "192.168.1.100")
        self.assertEqual(saved_packet.dst_ip, "10.0.0.1")
        self.assertEqual(saved_packet.src_port, 53)
        self.assertEqual(saved_packet.dst_port, 53)

    def test_advanced_packet_callback_icmp(self):
        # Test ICMP packet processing
        test_packet = self._create_test_packet(protocol="ICMP")

        with patch("django.utils.timezone.now", return_value=timezone.now()):
            advanced_packet_callback(test_packet)

        # Verify packet was saved
        saved_packet = Packet.objects.first()
        self.assertIsNotNone(saved_packet)
        self.assertEqual(saved_packet.protocol, "ICMP")
        self.assertEqual(saved_packet.src_ip, "192.168.1.100")
        self.assertEqual(saved_packet.dst_ip, "10.0.0.1")

    @patch("logging.error")
    def test_advanced_packet_callback_error_handling(self, mock_log_error):
        # Test error handling with an invalid packet
        invalid_packet = MagicMock(spec=ScapyPacket)
        invalid_packet.haslayer.return_value = False

        advanced_packet_callback(invalid_packet)

        # Verify no packet was saved and no error was logged
        self.assertEqual(Packet.objects.count(), 0)
        mock_log_error.assert_not_called()

    @patch("scapy.all.sniff")
    def test_capture_packets_on_interface(self, mock_sniff):
        # Test interface capture configuration
        config = PacketCaptureConfig()
        config.CAPTURE_INTERFACES = ["eth0"]
        config.MAX_PACKETS = 10
        config.FILTER = "tcp"
        config.TIMEOUT = 30

        capture_packets_on_interface("eth0", config)

        # Verify sniff was called with correct parameters
        mock_sniff.assert_called_once_with(
            iface="eth0",
            prn=advanced_packet_callback,
            store=0,
            filter="tcp",
            count=10,
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()
