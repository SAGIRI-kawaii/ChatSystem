import os
from io import BytesIO
import uvicorn
import hashlib
import datetime
from sqlalchemy import or_
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from sqlalchemy import desc, join

from .database.AsyncORM import *
from utils import *

IMAGE_BASE_PATH = "/Users/duyifan/Desktop/Code/Python/ChatSystem/static/"
IMAGE_NOT_FOUND_PATH = "/Users/duyifan/Desktop/Code/Python/ChatSystem/static/"

app = FastAPI(
    # docs_url=None,
    # redoc_url=None
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/user/register/")
async def register(username: str, password: str) -> dict:
    if await orm.fetchone(select(User.username).where(User.username == username)):
        return {"code": 403, "message": "Account already exists"}
    else:
        try:
            last_id = await orm.fetchone(select(User.user_id).order_by(desc(User.user_id)))
            new_id = last_id[0] + 1 if last_id else 10000000
            await orm.insert(
                User,
                {
                    "user_id": new_id,
                    "username": username,
                    "password": (hashlib.md5(password.encode("utf-8")).hexdigest()).upper()
                }
            )
            return {"code": 201, "message": "Registration success", "data": {"user_id": new_id}}
        except Exception as e:
            return {"code": 500, "message": str(e)}


@app.post("/user/login/")
async def login(password: str, username: str = None, user_id: str = None):
    if not username and not user_id:
        return {"code": 403, "message": "Username or user_id cannot be all empty"}
    try:
        md5_pass = (hashlib.md5(password.encode("utf-8")).hexdigest()).upper()
        if username:
            result = await orm.fetchone(
                select(
                    User.user_id
                ).where(
                    User.username == username
                )
            )
            if not result:
                return {"code": 402, "message": "User not found"}
            result = await orm.fetchone(
                select(
                    User.user_id
                ).where(
                    User.username == username,
                    User.password == md5_pass
                )
            )
            if result:
                user_info = await user_id_to_detail(result[0])
                user_info["cookie"] = get_salt(result[0])
                return {
                    "code": 200,
                    "message": "success",
                    "data": user_info
                }
            else:
                return {"code": 403, "message": "Wrong username or password"}
        if user_id:
            result = await orm.fetchone(
                select(
                    User.user_id
                ).where(
                    User.user_id == user_id
                )
            )
            if not result:
                return {"code": 402, "message": "User not found"}
            result = await orm.fetchone(
                select(
                    User.user_id
                ).where(
                    User.user_id == user_id,
                    User.password == md5_pass
                )
            )
            if result:
                return {"code": 200, "message": "success", "data": get_salt(result)}
            else:
                return {"code": 403, "message": "Wrong user_id or password"}
    except Exception as e:
        return {"code": 500, "message": str(e)}


@app.post("/user/modifyPersonalInformation/")
async def modify_personal_information(
        cookie: str,
        nickname: str = None,
        password: str = None,
        sign: str = None,
        avatar: str = None,
        avatar_bytes: bytes = None
) -> dict:
    pass


@app.post("/group/create")
async def create_group(operator_id: int, cookie: str):
    if not cookie_check(operator_id, cookie):
        return {"code": 401, "message": "Unauthorized"}
    try:
        last_id = await orm.fetchone(select(Group.group_id).order_by(desc(Group.group_id)))
        new_group_id = last_id[0] + 1 if last_id else 100000
        await orm.insert(Group, {"group_id": new_group_id})
        await orm.insert(GroupRelationship, {"group_id": new_group_id, "member_id": operator_id, "permission": 3})
        return {"code": 201, "message": "Group create successfully", "data": new_group_id}
    except Exception as e:
        return {"code": 500, "message": str(e)}


@app.post("/group/modifyGroupInformation/")
async def modify_group_information(
        cookie: str,
        name: str = None,
        description: str = None,
        avatar: str = None,
        avatar_bytes: bytes = None
) -> dict:
    pass


@app.post("/group/join/")
async def send_join_group_application(receiver_id: int, applicant_id: int, cookie: str, message: str = None):
    if not cookie_check(applicant_id, cookie):
        return {"code": 401, "message": "Unauthorized"}
    if await orm.fetchone(
        select(
            GroupRelationship.member_id
        ).where(
            GroupRelationship.group_id == receiver_id,
            GroupRelationship.member_id == applicant_id
        )
    ):
        return {"code": 403, "message": "The account is already in the group"}
    if await orm.fetchone(
        select(
            Application.receiver
        ).where(
            Application.applicant == applicant_id,
            Application.receiver == receiver_id,
            Application.application_type == 2
        )
    ):
        return {"code": 402, "message": "Request already exists"}
    else:
        try:
            await orm.insert(
                Application,
                {
                    "time": datetime.datetime.now(),
                    "applicant": applicant_id,
                    "receiver": receiver_id,
                    "message": message,
                    "application_type": 2
                }
            )
            return {"code": 201, "message": "Request sent successfully"}
        except Exception as e:
            return {"code": 500, "message": str(e)}


@app.post("/group/acceptApplication")
async def accept_application(account: int, cookie: str, applicant: int, group_id: int):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    permission = await get_member_permission_in_group(group_id, account)
    if not permission:
        return {"code": 403, "message": "Account is not in this group"}
    elif permission == 1:
        return {"code": 403, "message": "Permission denied"}
    if await orm.fetchone(
        select(
            GroupRelationship.member_id
        ).where(
            GroupRelationship.group_id == group_id,
            GroupRelationship.member_id == applicant
        )
    ):
        return {"code": 403, "message": "The account is already in the group"}
    if not await orm.fetchone(
        select(
            Application.applicant
        ).where(
            Application.applicant == applicant,
            Application.receiver == group_id,
            Application.application_type == 2,
            Application.passed == False
        )
    ):
        return {"code": 404, "message": "Application not found"}
    try:
        await orm.update(
            Application,
            [
                Application.applicant == applicant,
                Application.receiver == group_id,
                Application.application_type == 2,
                Application.passed == False
            ],
            {
                "passed": True
            }
        )
        await orm.insert_or_ignore(
            GroupRelationship,
            [
                GroupRelationship.group_id == group_id,
                GroupRelationship.member_id == applicant,
            ],
            {"group_id": group_id, "member_id": applicant}
        )
        return {"code": 200, "message": "success"}
    except Exception as e:
        return {"code": 500, "message": str(e)}


@app.post("/group/quit/")
async def quit_from_group(member_id: int, group_id: int, cookie: str):
    if not cookie_check(member_id, cookie):
        return {"code": 401, "message": "Unauthorized"}
    if not await orm.fetchone(
        select(
            GroupRelationship.member_id
        ).where(
            GroupRelationship.group_id == group_id,
            GroupRelationship.member_id == member_id
        )
    ):
        return {"code": 403, "message": "Account is not in this group"}
    else:
        try:
            await orm.insert(
                Application,
                {"time": datetime.datetime.now(), "applicant": member_id, "receiver": group_id, "application_type": 3}
            )
            await orm.delete(
                GroupRelationship,
                [GroupRelationship.group_id == group_id, GroupRelationship.member_id == member_id]
            )
            return {"code": 201, "message": "Exit successfully"}
        except Exception as e:
            return {"code": 500, "message": str(e)}


@app.post("/group/disband/")
async def disband_group(operator_id: int, group_id: int, cookie: str):
    if not cookie_check(operator_id, cookie):
        return {"code": 401, "message": "Unauthorized"}
    permission = await get_member_permission_in_group(group_id, operator_id)
    if not permission:
        return {"code": 403, "message": "Account is not in this group"}
    elif permission != 3:
        return {"code": 403, "message": "Permission denied"}
    else:
        try:
            await orm.delete(Group, [Group.group_id == group_id])
            await orm.delete(GroupRelationship, [GroupRelationship.group_id == group_id])
            return {"code": 201, "message": "Disband successfully"}
        except Exception as e:
            return {"code": 500, "message": str(e)}


@app.post("/friend/add/")
async def add_friend(applicant_id: int, receiver_id: int, cookie: str, message: str = None):
    if not cookie_check(applicant_id, cookie):
        return {"code": 401, "message": "Unauthorized"}
    if await orm.fetchone(
        select(
            FriendRelationship.account
        ).where(
            FriendRelationship.account == applicant_id,
            FriendRelationship.friend == receiver_id
        )
    ):
        return {"code": 403, "message": "This account is already your friend"}
    if await orm.fetchone(
        select(
            Application.receiver
        ).where(
            Application.applicant == applicant_id,
            Application.receiver == receiver_id,
            Application.application_type == 1
        )
    ):
        return {"code": 402, "message": "Request already exists"}
    else:
        try:
            await orm.insert(
                Application,
                {
                    "time": datetime.datetime.now(),
                    "applicant": applicant_id,
                    "receiver": receiver_id,
                    "application_type": 1,
                    "message": message
                }
            )
            return {"code": 201, "message": "Request sent successfully"}
        except Exception as e:
            return {"code": 500, "message": str(e)}


@app.post("/friend/acceptApplication")
async def accept_application(account: int, cookie: str, applicant: int):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    if not await orm.fetchone(
        select(
            Application.applicant
        ).where(
            Application.applicant == applicant,
            Application.receiver == account,
            Application.application_type == 1,
            Application.passed == False
        )
    ):
        return {"code": 404, "message": "Application not found"}
    try:
        await orm.update(
            Application,
            [
                Application.applicant == applicant,
                Application.receiver == account,
                Application.application_type == 1,
                Application.passed == False
            ],
            {
                "passed": True
            }
        )
        await orm.insert_or_ignore(
            FriendRelationship,
            [
                FriendRelationship.account == account,
                FriendRelationship.friend == applicant
            ],
            {"account": account, "friend": applicant}
        )
        await orm.insert_or_ignore(
            FriendRelationship,
            [
                FriendRelationship.account == applicant,
                FriendRelationship.friend == account
            ],
            {"account": applicant, "friend": account}
        )
        return {"code": 200, "message": "success"}
    except Exception as e:
        return {"code": 500, "message": str(e)}


@app.post("/friend/delete/")
async def delete_friend(operator_id: int, target_id: int, cookie: str):
    if not cookie_check(operator_id, cookie):
        return {"code": 401, "message": "Unauthorized"}
    if not await orm.fetchone(
        select(
            FriendRelationship.friend
        ).where(
            FriendRelationship.account == operator_id,
            FriendRelationship.friend == target_id
        )
    ):
        return {"code": 403, "message": "The account is not your friend"}
    else:
        try:
            await orm.delete(
                FriendRelationship,
                [
                    FriendRelationship.account == operator_id,
                    FriendRelationship.friend == target_id
                ]
            )
            await orm.delete(
                FriendRelationship,
                [
                    FriendRelationship.account == target_id,
                    FriendRelationship.friend == operator_id
                ]
            )
            return {"code": 201, "message": "Request sent successfully"}
        except Exception as e:
            return {"code": 500, "message": str(e)}


@app.get("/info/getJoinedGroups/")
async def get_joined_groups(account: int, cookie: str):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    try:
        result = await orm.fetchall(
            select(
                Group.group_id
            ).select_from(
                join(Group, GroupRelationship, Group.group_id == GroupRelationship.group_id)
            ).where(
                GroupRelationship.member_id == account
            )
        )
        if result:
            result = await group_id_to_detail([res[0] for res in result])
        return {"code": 200, "message": "success", "data": result}
    except Exception as e:
        return {"code": 500, "message": str(e)}


@app.get("/info/getFriends/")
async def get_friends(account: int, cookie: str):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    try:
        result = await orm.fetchall(
            select(
                User.user_id
            ).select_from(
                join(User, FriendRelationship, User.user_id == FriendRelationship.friend)
            ).where(
                FriendRelationship.account == account
            )
        )
        if result:
            result = await user_id_to_detail([res[0] for res in result])
        return {"code": 200, "message": "success", "data": result}
    except Exception as e:
        return {"code": 500, "message": str(e)}


@app.get("/info/friendApplications")
async def get_friend_applications(account: int, cookie: str):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    try:
        result = await orm.fetchall(
            select(
                Application.time,
                Application.applicant,
                Application.message
            ).where(
                Application.receiver == account,
                Application.application_type == 1,
                Application.passed == False
            )
        )
        print(result)
        result = [{"time": res.time, "applicant": await user_id_to_detail(res.applicant), "message": res.message} for res in result]
        return {"code": 200, "message": "success", "data": result}
    except Exception as e:
        return {"code": 500, "message": str(e)}


@app.get("/info/groupApplications")
async def get_group_applications(account: int, group_id: int, cookie: str):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    permission = await get_member_permission_in_group(group_id, account)
    if not permission:
        return {"code": 403, "message": "Account is not in this group"}
    elif permission == 1:
        return {"code": 403, "message": "Permission denied"}
    try:
        result = await orm.fetchall(
            select(
                Application.time,
                Application.applicant,
                Application.message
            ).where(
                Application.receiver == group_id,
                Application.application_type == 2,
                Application.passed == False
            )
        )
        print(result)
        result = [{"time": res.time, "applicant": await user_id_to_detail(res.applicant), "message": res.message} for res in result]
        print(result)
        return {"code": 200, "message": "success", "data": result}
    except Exception as e:
        return {"code": 500, "message": str(e)}


@app.get("/info/quitGroupMessages")
async def get_quit_group_messages(account: int, cookie: str):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    try:
        result = await orm.fetchall(
            select(
                Application.time,
                Application.applicant,
                Application.receiver
            ).select_from(
                join(GroupRelationship, Application, Application.receiver == GroupRelationship.group_id)
            ).where(
                GroupRelationship.member_id == account,
                GroupRelationship.permission > 1,
                Application.application_type == 3
            )
        )
        result = [
            {
                "time": res.time,
                "applicant": await user_id_to_detail(res.applicant),
                "group": await group_id_to_detail(res.receiver)
            } for res in result
        ]
        return {"code": 200, "message": "success", "data": result if result else []}
    except Exception as e:
        return {"code": 500, "message": str(e)}


@app.get("/info/groupMembers")
async def get_group_members(account: int, cookie: str, group_id: int):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    if not await user_in_group(group_id, account):
        return {"code": 403, "message": "Account is not in this group"}
    try:
        result = await orm.fetchall(
            select(
                GroupRelationship.member_id,
                GroupRelationship.permission
            ).where(
                GroupRelationship.group_id == group_id
            )
        )
        owner = {}
        admin = []
        member = []
        for res in result:
            if res.permission == 3:
                owner = await user_id_to_detail(res.member_id)
            elif res.permission == 2:
                admin.append(await user_id_to_detail(res.member_id))
            elif res.permission == 1:
                member.append(await user_id_to_detail(res.member_id))
        return {"code": 200, "message": "success", "data": {"owner": owner, "admin": admin, "member": member}}
    except Exception as e:
        return {"code": 500, "message": str(e)}


@app.get("/info/user/")
async def get_user_info(account: int, cookie: str, target: int):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    try:
        return {"code": 200, "message": "success", "data": await user_id_to_detail(target)}
    except UserNotExist:
        return {"code": 403, "message": "User not exist"}


@app.get("/info/group/")
async def get_group_info(account: int, cookie: str, target: int):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    try:
        return {"code": 200, "message": "success", "data": await group_id_to_detail(target)}
    except GroupNotExist:
        return {"code": 403, "message": "Group not exist"}


@app.get("/image/exist/")
async def image_exist(account: int, cookie: str, image_md5: str):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    path = os.path.join(IMAGE_BASE_PATH, image_md5 + ".png")
    return {"code": 200, "message": "success", "data": os.path.exists(path)}


@app.get("/image/upload/")
async def image_exist(account: int, cookie: str, image_content: bytes, image_md5: str):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    if not image_md5_check(image_content, image_md5):
        return {"code": 403, "message": "The picture does not match the md5 value"}
    path = os.path.join(IMAGE_BASE_PATH, image_md5 + ".png")
    return {"code": 200, "message": "success", "data": os.path.exists(path)}


@app.get("/info/chatData/")
async def get_chat_data(account: int, cookie: str):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized"}
    group_result = await orm.fetchall(
        select(
            GroupChatRecord.time,
            GroupChatRecord.sender,
            GroupChatRecord.group_id,
            GroupChatRecord.message_chain
        ).select_from(
                join(GroupChatRecord, GroupRelationship, GroupChatRecord.group_id == GroupRelationship.group_id)
        ).where(
            GroupRelationship.member_id == account
        ).order_by(
            GroupChatRecord.time
        )
    )
    friend_result = await orm.fetchall(
        select(
            FriendChatRecord.time,
            FriendChatRecord.sender,
            FriendChatRecord.receiver,
            FriendChatRecord.message_chain
        ).where(
            or_(FriendChatRecord.receiver == account, FriendChatRecord.sender == account)
        )
    )
    return {
        "code": 200,
        "message": "success",
        "data": {
            "group": [{"time": i[0], "sender": i[1], "group_id": i[2], "messageChain": json.loads(i[3])} for i in group_result],
            "friend": [{"time": i[0], "sender": i[1], "recevier": i[2], "messageChain": json.loads(i[3])} for i in friend_result]
        }
    }


@app.get("/user/cookieCheck/")
async def get_cookie_check(account: int, cookie: str):
    if not cookie_check(account, cookie):
        return {"code": 401, "message": "Unauthorized", "data": False}
    else:
        return {"code": 200, "message": "success", "data": True}


@app.get("/user/exist/")
async def user_exist(user_id: int):
    result = await orm.fetchone(select(User.user_id).where(User.user_id == user_id))
    return {"code": 200, "message": "success", "data": True if result else False}


@app.get("/image/get/{image_md5}")
async def get_image(image_md5: str):
    path = os.path.join(IMAGE_BASE_PATH, f"{image_md5}.png")
    if os.path.exists(path):
        with open(path, "rb") as r:
            return StreamingResponse(BytesIO(r.read()), media_type="image/png")
    else:
        return {"code": 404, "message": "File not exist!"}


@app.get("/info/idType/")
async def id_to_type(id: int):
    return {"code": 200, "message": "success", "data": "Group" if len(str(id)) == 6 else "Friend"}


# @app.get("/info/allAvatar")
# async def get_all_avatar(account: int, cookie: str):
#     result = {"userData": {}, "groupData": {}}
#     users = await orm.fetchall(
#         select(
#             User.user_id,
#             User.username,
#             User.nickname,
#             User.sign,
#             User.avatar
#         ).select_from(
#             join(User, FriendRelationship, User.user_id == FriendRelationship.friend)
#         ).where(
#             FriendRelationship.account == account
#         )
#     )
#     # print(users)
#     for user in users:
#         result["userData"][user.user_id] = {
#             "user_id": User.user_id,
#             "username": User.username,
#             "nickname": User.nickname,
#             "sign": User.sign,
#             "avatar": User.avatar,
#         }
#     groups = await orm.fetchall(
#         select(
#             Group.group_id,
#             Group.name,
#             Group.description,
#             Group.avatar
#         ).select_from(
#             join(Group, GroupRelationship, Group.group_id == GroupRelationship.group_id)
#         ).where(
#             GroupRelationship.member_id == account
#         )
#     )
#     for group in groups:
#         result["groupData"][group.group_id] = {
#             "group_id": group.group_id,
#             "name": group.name,
#             "description": group.description,
#             "avatar": group.avatar,
#         }
#     print(groups)
#     return {"code": 200, "message": "success", "data": result}


def run_api():
    uvicorn.run(app, host="127.0.0.1", port=12345)
#     , log_level="error"
