from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_update(data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "dashboard", {"type": "dashboard_update", "data": data}
    )
