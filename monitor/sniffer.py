

from scapy.all import sniff, TCP, UDP, ICMP, IP
from .models import Packet
def packet_callback(packet):
    try:
        summary = ""
        ip_layer = None

        if packet.haslayer(IP):
            ip_layer = packet.getlayer(IP)
            summary = f"IP: {ip_layer.src} -> {ip_layer.dst}"

            if packet.haslayer(TCP) and ip_layer:
                tcp_layer = packet.getlayer(TCP)
                summary = f"TCP: {ip_layer.src}:{tcp_layer.sport} -> {ip_layer.dst}:{tcp_layer.dport}"
            elif packet.haslayer(UDP) and ip_layer:
                udp_layer = packet.getlayer(UDP)
                summary = f"UDP: {ip_layer.src}:{udp_layer.sport} -> {ip_layer.dst}:{udp_layer.dport}"
            elif packet.haslayer(ICMP) and ip_layer:
                icmp_layer = packet.getlayer(ICMP)
                summary = f"ICMP: {ip_layer.src} -> {ip_layer.dst} Type: {icmp_layer.type}"

            # Store packet in database
            Packet.objects.create(summary=summary)
            
    except Exception as e:
        logger.error(f"Error processing packet: {str(e)}", exc_info=True)

def start_sniffing():
    # Sniff packets and call packet_callback for each packet
    sniff(prn=packet_callback, store=0)  # store=0 to avoid memory issues