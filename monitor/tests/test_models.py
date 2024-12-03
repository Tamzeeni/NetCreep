import pytest
from django.test import TestCase
from monitor.models import NetworkInterface, PacketCapture, AlertThreshold

class TestNetworkModels(TestCase):
    def setUp(self):
        # Create test data
        self.interface = NetworkInterface.objects.create(
            name="Test Interface",
            description="A test network interface"
        )
        
        self.packet = PacketCapture.objects.create(
            interface=self.interface,
            protocol="TCP",
            source_ip="192.168.1.100",
            destination_ip="10.0.0.1",
            source_port=8080,
            destination_port=443,
            packet_size=1024
        )
        
        self.threshold = AlertThreshold.objects.create(
            name="High Traffic Alert",
            metric="packet_count",
            threshold_value=1000,
            severity="high"
        )

    def test_network_interface_creation(self):
        """Test NetworkInterface model creation."""
        self.assertEqual(self.interface.name, "Test Interface")
        self.assertTrue(self.interface.is_active)

    def test_packet_capture_creation(self):
        """Test PacketCapture model creation."""
        self.assertEqual(self.packet.protocol, "TCP")
        self.assertEqual(self.packet.source_ip, "192.168.1.100")

    def test_alert_threshold_creation(self):
        """Test AlertThreshold model creation."""
        self.assertEqual(self.threshold.name, "High Traffic Alert")
        self.assertEqual(self.threshold.severity, "high")

    def test_model_string_representations(self):
        """Test string representations of models."""
        self.assertEqual(str(self.interface), "Test Interface")
        self.assertTrue(str(self.packet).startswith("TCP packet"))
        self.assertEqual(str(self.threshold), "High Traffic Alert - packet_count threshold")
