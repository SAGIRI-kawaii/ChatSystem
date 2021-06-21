import json
import datetime

from utils import *
from .data import account_ws
from .database.AsyncORM import *


async def group_message_broadcast(data: dict, time):
    members = await orm.fetchall(select(GroupRelationship.member_id).where(GroupRelationship.group_id == data["target"]))
    print(members)
    # print(json.dumps({
    #             "type": "group",
    #             "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    #             "messageChain": data["messageChain"],
    #             "sender": {
    #                 ** (await user_id_to_detail(data["account"]))
    #             },
    #             "group": await group_id_to_detail(data["target"])
    #         }, indent=4))
    for member in members:
        if member[0] in account_ws and member[0] != data["account"]:
            print(member[0])
            await account_ws[member[0]].send(json.dumps({
                "type": "group",
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "messageChain": data["messageChain"],
                "sender": {
                    ** (await user_id_to_detail(data["account"]))
                },
                "group": await group_id_to_detail(data["target"])
            }))


async def send_group_message(data: dict):
    time_now = datetime.datetime.now()
    print(data)
    # print(json.dumps(data["messageChain"]))
    await orm.insert(
        GroupChatRecord,
        {
            "time": time_now,
            "group_id": data["target"],
            "sender": data["account"],
            "message_chain": json.dumps(data["messageChain"])
        }
    )
    await group_message_broadcast(data, time_now)


async def send_friend_message(data: dict):
    time_now = datetime.datetime.now()
    await orm.insert(
        FriendChatRecord,
        {
            "time": time_now,
            "sender": data["account"],
            "receiver": data["target"],
            "message_chain": json.dumps(data["messageChain"])
        }
    )
    print({
            "type": "friend",
            "messageChain": data["messageChain"],
            "sender": await user_id_to_detail(data["account"])
        })
    if data["target"] in account_ws:
        await account_ws[data["target"]].send(json.dumps({
            "time": time_now.strftime("%Y-%m-%d %H:%M:%S"),
            "type": "friend",
            "messageChain": data["messageChain"],
            "sender": await user_id_to_detail(data["account"])
        }))


async def hello(data: dict):
    time_now = datetime.datetime.now()
    await account_ws[data["account"]].send(json.dumps({
        "time": time_now.strftime("'%Y-%m-%d %H:%M:%S'"),
        "type": "hello"
    }))


handle = {
    "SendGroupMessage": send_group_message,
    "SendFriendMessage": send_friend_message,
    "Hello": hello
}