import json
import asyncio
import datetime
import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosed

from .handler import handle
from .data import account_ws, ws_account
from utils import cookie_check

"""
消息报文格式
群组消息
{
    "type": "group",
    "time": "2021-05-23",
    "messageChain": [
        {
            "type": "Plain",
            "content": "Mirai牛逼",
            "display": "Mirai牛逼"
        }
    ],
    "sender": {
        "user_id": 10000001,
        "username": "sagiri",
        "nickname": "sagiri",
        "sign": "这个人很懒，没有留下任何东西",
        "avatar": null
    },
    "group": {
        "group_id": 100001,
        "name": "世界第一小可爱纱雾酱",
        "description": "本群还没有描述呢～快来编辑吧～",
        "avatar": null
    }
}
好友消息
{
    "type": "friend",
    "messageChain": [
        {
            "type": "Source",
            "id": 123456,
            "time": 123456789
        },
        {
            "type": "Plain",
            "text": "Miral牛逼"
        }
    ],
    "sender": {
        "user_id": 10000001,
        "username": "sagiri",
        "nickname": "sagiri",
        "sign": "这个人很懒，没有留下任何东西",
        "avatar": null
    }
}
事件报文格式
被踢出群
{
    "type": "AccountLeaveEventKick",
    "group": {
        "group_id": 100001,
        "name": "世界第一小可爱纱雾酱",
        "description": "本群还没有描述呢～快来编辑吧～",
        "avatar": null
    }
}
成员权限改变
{
    "type": "MemberPermissionChangeEvent",
    "origin": "MEMBER",
    "new": "ADMINISTRATOR",
    "current": "ADMINISTRATOR",
    "member": {
        "user_id": 10000001,
        "username": "sagiri",
        "nickname": "sagiri",
        "sign": "这个人很懒，没有留下任何东西",
        "avatar": null
        "group": {
            "group_id": 100001,
            "name": "世界第一小可爱纱雾酱",
            "description": "本群还没有描述呢～快来编辑吧～",
            "avatar": null
        }
    }
}
好友申请
{
    "type": "NewFriendRequestEvent",
    "applicant": {    
        "user_id": 10000001,
        "username": "sagiri",
        "nickname": "sagiri",
        "sign": "这个人很懒，没有留下任何东西",
        "message": ""
    }
}
入群申请
{
    "type": "MemberJoinRequestEvent",
    "fromId": 10000001,
    "group": {
        "group_id": 100001,
        "name": "世界第一小可爱纱雾酱",
        "description": "本群还没有描述呢～快来编辑吧～",
        "avatar": null
    }
    "applicant": {    
        "user_id": 10000001,
        "username": "sagiri",
        "nickname": "sagiri",
        "sign": "这个人很懒，没有留下任何东西",
        "message": ""
    }
}
发送消息
{   
    "type": "SendGroupMessage",
    "account": 123,
    "cookie": "cookie",
    "target": 123456,
    "messageChain": [
        { "type": "Plain", "text": "hello\n" },
        { "type": "Plain", "text": "world" },
        { "type": "Image", "url": "https://i0.hdslb.com/bfs/album/67fc4e6b417d9c68ef98ba71d5e79505bbad97a1.png" }
    ]
}
{   
    "type": "SendFriendMessage",
    "account": 123,
    "cookie": "cookie",
    "target": 123456,
    "messageChain": [
        { "type": "Plain", "text": "hello\n" },
        { "type": "Plain", "text": "world" },
        { "type": "Image", "url": "https://i0.hdslb.com/bfs/album/67fc4e6b417d9c68ef98ba71d5e79505bbad97a1.png" }
    ]
}
"""


async def message_handle(websocket, path):
    while True:
        try:
            message = await websocket.recv()
        except (ConnectionClosed, ConnectionClosedOK):
            account = ws_account[websocket]
            del account_ws[account]
            del ws_account[websocket]
        print(account_ws)
        if isinstance(message, bytes):
            message = message.decode("utf-8")
        print("received:", message)
        if not isinstance(message, dict):
            message = json.loads(message)
        # print("json:", message)
        if not cookie_check(message["account"], message["cookie"]):
            await websocket.send(json.dumps({"code": 401, "message": "Unauthorized"}).encode("utf-8"))
        if message["account"] not in account_ws:
            account_ws[message["account"]] = websocket
            ws_account[websocket] = message["account"]
        elif account_ws[message["account"]] != websocket:
            account_ws[message["account"]] = websocket
            ws_account[websocket] = message["account"]
        if message["type"] in handle:
            await handle[message["type"]](message)
            await websocket.send(json.dumps({"code": 200, "message": "success"}).encode("utf-8"))
        else:
            await websocket.send(json.dumps({"code": 403, "message": "Unknown event"}).encode("utf-8"))
        # except Exception as e:
        #     await websocket.send(str(e).encode("utf-8"))
        #     print(e)


start_server = websockets.serve(message_handle, "127.0.0.1", 12346)
# asyncio.get_event_loop().run_until_complete(start_server)
