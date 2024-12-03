import pytest
from unittest.mock import patch, MagicMock
from monitor.sniffer import PacketCaptureManager
from scapy.packet import Packet as ScapyPacket
from scapy.layers.inet import IP, TCP

class TestPacketCaptureManager:
    def test_initialization(self):
        """Test PacketCaptureManager initialization."""
        manager = PacketCaptureManager()
        assert manager.interfaces is not None
        assert len(manager.interfaces) > 0
        assert not manager.capture_processes
        assert manager.consumer_process is None

    @patch('monitor.sniffer.multiprocessing.Queue')
    def test_queue_creation(self, mock_queue):
        """Test packet queue creation."""
        manager = PacketCaptureManager()
        mock_queue.assert_called_once_with(maxsize=10000)

    def test_get_network_interfaces(self):
        """Test network interface detection."""
        manager = PacketCaptureManager()
        interfaces = manager._get_network_interfaces()
        assert isinstance(interfaces, list)
        assert len(interfaces) > 0

    @patch('monitor.sniffer.multiprocessing.Process')
    def test_start_capture(self, mock_process):
        """Test starting packet capture."""
        manager = PacketCaptureManager()
        manager.start_capture()
        
        # Verify processes were created
        assert len(manager.capture_processes) > 0
        assert manager.consumer_process is not None

    def test_stop_capture(self):
        """Test stopping packet capture."""
        manager = PacketCaptureManager()
        manager.start_capture()
        manager.stop_capture()

        # Verify stop event is set and processes are terminated
        assert manager.stop_event.is_set()
        
    def test_process_packet(self):
        """Test packet processing method."""
        manager = PacketCaptureManager()
        
        # Create a mock Scapy packet
        mock_packet = IP(src='192.168.1.100', dst='10.0.0.1')/TCP(sport=8080, dport=443)
        
        processed_packet = manager._process_packet(mock_packet)
        
        # Verify packet processing
        assert processed_packet is not None
        assert 'timestamp' in processed_packet
        assert processed_packet['source_ip'] == '192.168.1.100'
        assert processed_packet['destination_ip'] == '10.0.0.1'
        assert processed_packet['protocol'] == 'TCP'
