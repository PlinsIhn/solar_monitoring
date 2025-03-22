import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SensorDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connexion WebSocket"""
        self.room_name = "sensor_data"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Déconnexion WebSocket"""
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        """Cette fonction ne sert plus à sauvegarder des données"""
        pass

    async def send_sensor_data(self, event):
        """Envoi automatique des données mises à jour"""
        await self.send(text_data=json.dumps(event["data"]))
