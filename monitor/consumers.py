import asyncio
import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("New client connecting")
        await self.channel_layer.group_add("dashboard", self.channel_name)
        await self.accept()
        logger.info("Client connected successfully")

        # Start sending periodic updates
        self.send_updates_task = asyncio.create_task(self.send_periodic_updates())

    async def disconnect(self, close_code):
        logger.info(f"Client disconnected with code: {close_code}")
        if hasattr(self, "send_updates_task"):
            self.send_updates_task.cancel()
        await self.channel_layer.group_discard("dashboard", self.channel_name)

    async def send_periodic_updates(self):
        while True:
            try:
                stats = await self.get_system_stats()
                logger.debug(f"Sending stats: {stats}")
                await self.send(text_data=json.dumps(stats))
            except Exception as e:
                logger.error(f"Error sending stats: {e}")
            await asyncio.sleep(1)  # Update every second

    @database_sync_to_async
    def get_system_stats(self):
        from .system_monitor import get_system_stats

        return get_system_stats()

    async def receive(self, text_data):
        logger.debug(f"Received message: {text_data}")

    async def dashboard_update(self, event):
        logger.debug(f"Broadcasting update: {event['data']}")
        await self.send(text_data=json.dumps(event["data"]))
