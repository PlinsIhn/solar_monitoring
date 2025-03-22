import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChannelData

@receiver(post_save, sender=ChannelData)
def send_sensor_data(sender, instance, **kwargs):
    """Envoie les nouvelles données du capteur via WebSocket dès qu'elles sont mises à jour."""
    channel_layer = get_channel_layer()

    # Récupère la dernière valeur du capteur
    data = {
        "channel": instance.channel.name,
        "value": instance.value,
        "timestamp": instance.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Envoi des données au groupe WebSocket
    async_to_sync(channel_layer.group_send)(
        "sensor_data",  # Doit correspondre au nom du groupe dans le consumer
        {
            "type": "send_sensor_data",
            "data": data,
        }
    )
