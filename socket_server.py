import asyncio

from server.websocket import start_server


asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
