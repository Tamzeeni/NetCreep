import logging
import multiprocessing
import os
import queue
import signal
import time
from typing import Any, Dict, List, Optional

import psutil
from django.conf import settings
from django.utils import timezone
from scapy.all import ICMP, IP, TCP, UDP, sniff
from scapy.layers.inet6 import IPv6
from scapy.packet import Packet as ScapyPacket

from .models import Packet

logger = logging.getLogger(__name__)


class PacketCaptureManager:
    """Advanced packet capture management with multiprocessing."""

    def __init__(
        self,
        interfaces: List[str] = None,
        max_queue_size: int = 10000,
        max_packet_store: int = 50000,
    ):
        """
        Initialize packet capture manager.

        Args:
            interfaces (List[str]): Network interfaces to capture
            max_queue_size (int): Maximum size of packet processing queue
            max_packet_store (int): Maximum number of packets to store in database
        """
        self.interfaces = interfaces or self._get_network_interfaces()
        self.packet_queue = multiprocessing.Queue(maxsize=max_queue_size)
        self.max_packet_store = max_packet_store
        self.capture_processes: List[multiprocessing.Process] = []
        self.consumer_process: Optional[multiprocessing.Process] = None
        self.stop_event = multiprocessing.Event()

    @staticmethod
    def _get_network_interfaces() -> List[str]:
        """
        Dynamically detect available network interfaces.

        Returns:
            List of network interface names
        """
        try:
            if os.name == 'nt':  # Windows
                from scapy.arch.windows import get_windows_if_list
                interfaces = get_windows_if_list()
                return [iface['name'] for iface in interfaces if iface['name']]
            else:  # Linux/Unix
                return [
                    iface
                    for iface, addrs in psutil.net_if_addrs().items()
                    if any(addr.family == 2 for addr in addrs)  # IPv4 interfaces
                ]
        except Exception as e:
            logger.error(f"Interface detection error: {e}")
            return ["Wi-Fi"]  # Default to Wi-Fi on Windows

    def _packet_capture_worker(self, interface: str):
        """
        Packet capture worker for a specific interface.

        Args:
            interface (str): Network interface to capture packets on
        """

        def safe_packet_callback(packet: ScapyPacket):
            try:
                if not packet.haslayer(IP) and not packet.haslayer(IPv6):
                    return

                ip_layer = packet.getlayer(IP) or packet.getlayer(IPv6)
                protocol = "OTHER"
                src_port = None
                dst_port = None

                if packet.haslayer(TCP):
                    protocol = "TCP"
                    tcp_layer = packet.getlayer(TCP)
                    src_port = tcp_layer.sport
                    dst_port = tcp_layer.dport
                elif packet.haslayer(UDP):
                    protocol = "UDP"
                    udp_layer = packet.getlayer(UDP)
                    src_port = udp_layer.sport
                    dst_port = udp_layer.dport
                elif packet.haslayer(ICMP):
                    protocol = "ICMP"

                packet_data = {
                    "timestamp": timezone.now(),
                    "summary": f"{protocol}: {ip_layer.src}:{src_port or 'N/A'} -> {ip_layer.dst}:{dst_port or 'N/A'}",
                    "protocol": protocol,
                    "source_ip": str(ip_layer.src),
                    "destination_ip": str(ip_layer.dst),
                    "source_port": src_port,
                    "destination_port": dst_port,
                    "packet_size": len(packet),
                }

                try:
                    self.packet_queue.put(packet_data, block=False)
                except queue.Full:
                    logger.warning(
                        f"Packet queue full, dropping packet from {interface}"
                    )

            except Exception as e:
                logger.error(
                    f"Packet processing error on {interface}: {e}", exc_info=True
                )

        try:
            logger.info(f"Starting packet capture on {interface}")
            sniff(
                iface=interface,
                prn=safe_packet_callback,
                store=0,
                stop_filter=lambda x: self.stop_event.is_set(),
            )
        except Exception as e:
            logger.error(f"Capture error on {interface}: {e}")

    def _packet_consumer_worker(self):
        """
        Consume packets from queue and save to database.
        Implements intelligent packet storage management.
        """
        while not self.stop_event.is_set():
            try:
                packet_data = self.packet_queue.get(timeout=1)

                # Check total packet count before saving
                total_packets = Packet.objects.count()
                if total_packets >= self.max_packet_store:
                    # Delete oldest packets first
                    oldest_packets = Packet.objects.order_by("timestamp")[
                        : total_packets - self.max_packet_store + 1
                    ]
                    oldest_packets.delete()

                Packet.objects.create(**packet_data)
            except queue.Empty:
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Packet consumer error: {e}")

    def start_capture(self):
        """Start packet capture on multiple interfaces."""
        self.stop_event.clear()

        # Start capture processes for each interface
        for interface in self.interfaces:
            process = multiprocessing.Process(
                target=self._packet_capture_worker, args=(interface,)
            )
            process.start()
            self.capture_processes.append(process)

        # Start consumer process
        self.consumer_process = multiprocessing.Process(
            target=self._packet_consumer_worker
        )
        self.consumer_process.start()

        logger.info(f"Packet capture started on interfaces: {self.interfaces}")

    def stop_capture(self):
        """Gracefully stop packet capture."""
        self.stop_event.set()

        # Terminate capture processes
        for process in self.capture_processes:
            process.join(timeout=5)
            if process.is_alive():
                process.terminate()

        # Terminate consumer process
        if self.consumer_process:
            self.consumer_process.join(timeout=5)
            if self.consumer_process.is_alive():
                self.consumer_process.terminate()

        logger.info("Packet capture stopped")


def start_sniffing():
    """
    Global function to start packet capture.
    Uses environment variables for configuration.
    """
    interfaces = os.environ.get("NETCREEP_CAPTURE_INTERFACES", "eth0").split(",")
    max_packets = int(os.environ.get("NETCREEP_MAX_PACKETS", 50000))

    capture_manager = PacketCaptureManager(
        interfaces=interfaces, max_packet_store=max_packets
    )

    try:
        capture_manager.start_capture()
        return capture_manager
    except Exception as e:
        logger.error(f"Failed to start packet capture: {e}")
        return None
