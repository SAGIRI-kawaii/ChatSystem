import json
import asyncio
import websockets


async def send_msg(websocket):
    await websocket.send(json.dumps({
        "type": "SendGroupMessage",
        "account": 10000003,
        "cookie": "testCookie",
        "target": 100002,
        "messageChain": [
            {"type": "Plain", "content": "测试2from local\n", "display": "测试2from local\n"}
        ]
    }).encode("utf-8"))
    recv_text = await websocket.recv()
    print(f"{recv_text}")


async def main_logic():
    async with websockets.connect('ws://140.143.34.178:12346') as websocket:
        await send_msg(websocket)


asyncio.get_event_loop().run_until_complete(main_logic())
