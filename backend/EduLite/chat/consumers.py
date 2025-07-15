""" Testing Websocket """
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            "message": "Websocket connection established!"
        }))

    async def receive(self, text_data):
        # Echo back the received message
        await self.send(text_data=json.dumps({
            "echo": text_data
        }))

    async def disconnect(self, close_code):
        pass
