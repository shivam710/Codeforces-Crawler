import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer, SyncConsumer
from channels.db import database_sync_to_async
from .models import *
import datetime


class ChatConsumer(AsyncConsumer):

    async def websocket_connect(self,event):
        user1 = self.scope['url_route']['kwargs']['user1']
        user2 = self.scope['url_route']['kwargs']['user2']

        chat_room = f"chat_" + str(min(user1,user2)) + "_" + str(max(user1,user2))
        model_chatroom = Chatroom.objects.get(user1=min(user1,user2), user2=max(user1,user2))
        self.model_chatroom = model_chatroom

        self.chat_room = chat_room

        # docker_part
        # await self.channel_layer.group_add(
        #     self.chat_room,
        #     self.channel_name
        # )

        await self.send({
            "type": "websocket.accept",  # open WS.onopen
        })


    async def websocket_receive(self,event):

        front_text = event.get('text', None)
        msg = None
        if front_text is not None:
            load_dict_data = json.loads(front_text)
            msg = load_dict_data.get('message')
        print("falak receive", msg)
        user = self.scope['user']
        username = user.username

        myfinaldata = {
            'message': msg,
            'username': username
        }

        await self.create_chatmessage(user, msg)

        # docker
        # broadcast the message
        # await self.channel_layer.group_send(
        #     self.chat_room,
        #     {
        #         "type": "chat_message",
        #         "text": json.dumps(myfinaldata)
        #     }
        # )

        # non docker
        await self.send({
            "type": "websocket.send",  # send to ws.onmessage
            "text": json.dumps(myfinaldata)
        })


        print("falak receive", event)



    async def websocket_disconnect(self,event):
        print("falak disconnect", event)

    #docker part
    # sends actual message
    # def chat_message(self, event):
    #     await self.send({
    #         "type": "websocket.send",  # send to ws.onmessage
    #         "text": event['text']
    #     })

    @database_sync_to_async
    def create_chatmessage(self,user,msg):
        print("sssssssssssssssss", msg)
        if msg is "":
            print("sssssssssssssssss", msg)
            return False
        return Chatmessage.objects.create(chatroom=self.model_chatroom, user=user, message=msg)