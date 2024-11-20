from scapy.all import sniff, TCP, UDP, ICMP, IP
from .models import Packet
from django.utils import timezone
import logging 


logger = logging.getLogger(__name__)


def packet_callback(packet):
    try:
        if packet.haslayer(IP):
            ip_layer = packet.getlayer(IP)
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

            Packet.objects.create(
                summary=f"{protocol}: {ip_layer.src}:{src_port} -> {ip_layer.dst}:{dst_port}",
                protocol=protocol,
                src_ip=ip_layer.src,
                dst_ip=ip_layer.dst,
                src_port=src_port,
                dst_port=dst_port,
                size=len(packet)
            )
            
    except Exception as e:
        logger.error(f"Error processing packet: {str(e)}", exc_info=True)

def start_sniffing():
    # Sniff packets and call packet_callback for each packet
    sniff(prn=packet_callback, store=0)  # store=0 to avoid memory issues