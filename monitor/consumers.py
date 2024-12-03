import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SystemStat, Packet

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("dashboard", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("dashboard", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")
        
        if message_type == "get_stats":
            stats = await self.get_system_stats()
            await self.send(text_data=json.dumps({
                "type": "system_stats",
                "data": stats
            }))
        elif message_type == "get_packets":
            packets = await self.get_recent_packets()
            await self.send(text_data=json.dumps({
                "type": "recent_packets",
                "data": packets
            }))

    async def dashboard_update(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_system_stats(self):
        try:
            latest_stat = SystemStat.objects.latest("timestamp")
            return {
                "cpu_usage": latest_stat.cpu_usage,
                "memory_usage": latest_stat.memory_usage,
                "disk_usage": latest_stat.disk_usage,
                "network_in": latest_stat.network_in,
                "network_out": latest_stat.network_out,
                "timestamp": latest_stat.timestamp.isoformat()
            }
        except SystemStat.DoesNotExist:
            return None

    @database_sync_to_async
    def get_recent_packets(self):
        packets = Packet.objects.all().order_by("-timestamp")[:10]
        return [{
            "timestamp": packet.timestamp.isoformat(),
            "protocol": packet.protocol,
            "source": f"{packet.source_ip}:{packet.source_port}",
            "destination": f"{packet.destination_ip}:{packet.destination_port}",
            "size": packet.packet_size
        } for packet in packets]
