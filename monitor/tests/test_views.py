from django.test import TestCase, Client
from django.urls import reverse
from monitor.models import Packet, SystemStat, NetworkInterface

class TestMonitorViews(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test data
        self.interface = NetworkInterface.objects.create(
            name="Test Interface",
            is_active=True
        )
        Packet.objects.create(
            interface=self.interface,
            protocol="TCP",
            source_ip="192.168.1.100",
            destination_ip="10.0.0.1",
            source_port=8080,
            destination_port=443,
            packet_size=1024
        )
        SystemStat.objects.create(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=70.0,
            network_in=1000,
            network_out=2000
        )

    def test_dashboard_view(self):
        """Test dashboard view returns 200 and contains expected context."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('recent_packets', response.context)
        self.assertIn('packet_count', response.context)
        self.assertIn('latest_stats', response.context)

    def test_packet_history_view(self):
        """Test packet history view returns 200 and contains packets."""
        response = self.client.get(reverse('packet_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['packets']) > 0)

    def test_system_stats_view(self):
        """Test system stats view returns 200 and contains stats."""
        response = self.client.get(reverse('system_stats'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('stats', response.context)
