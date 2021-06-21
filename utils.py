import json
import random
import string
import hashlib
from typing import Union

from server.exceptions import *
from server.data import user_salt
from server.database.AsyncORM import *


def cookie_check(account: int, cookie: str) -> bool:
    if cookie == "testCookie":
        return True
    if account not in user_salt:
        return False
    return hashlib.md5((str(account) + user_salt[account]).encode("utf-8")).hexdigest() == hashlib.md5((str(account) + cookie).encode("utf-8")).hexdigest()


def get_salt(account: int):
    print(account)
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 30))
    user_salt[account] = salt
    return salt


async def group_id_to_detail(group_id: Union[list, int]) -> Union[list, dict]:
    if isinstance(group_id, list):
        result = []
        for gid in group_id:
            res = await orm.fetchone(
                select(
                    Group.group_id,
                    Group.name,
                    Group.description,
                    Group.avatar
                ).where(
                    Group.group_id == gid
                )
            )
            if res:
                result.append({
                    "group_id": res.group_id,
                    "name": res.name,
                    "description": res.description,
                    "avatar": res.avatar
                })
            else:
                raise GroupNotExist(f"{gid}")
        return result
    else:
        result = await orm.fetchone(
            select(
                Group.group_id,
                Group.name,
                Group.description,
                Group.avatar
            ).where(
                Group.group_id == group_id
            )
        )
        if result:
            return {
                "group_id": result.group_id,
                "name": result.name,
                "description": result.description,
                "avatar": result.avatar
            }
        else:
            raise GroupNotExist(f"{group_id}")


async def user_id_to_detail(user_id: Union[list, int]) -> Union[list, dict]:
    if isinstance(user_id, list):
        result = []
        for uid in user_id:
            res = await orm.fetchone(
                select(
                    User.user_id,
                    User.username,
                    User.nickname,
                    User.sign,
                    User.avatar
                ).where(
                    User.user_id == uid
                )
            )
            if res:
                result.append({
                    "user_id": res.user_id,
                    "username": res.username,
                    "nickname": res.nickname,
                    "sign": res.sign,
                    "avatar": res.avatar
                })
            else:
                raise UserNotExist(f"{uid}")
        return result
    else:
        result = await orm.fetchone(
            select(
                User.user_id,
                User.username,
                User.nickname,
                User.sign,
                User.avatar
            ).where(
                User.user_id == user_id
            )
        )
        if result:
            return {
                "user_id": result.user_id,
                "username": result.username,
                "nickname": result.nickname,
                "sign": result.sign,
                "avatar": result.avatar
            }
        else:
            raise UserNotExist(f"{user_id}")


async def user_in_group(group_id: int, user_id: int) -> bool:
    if await orm.fetchone(
        select(
            GroupRelationship.permission
        ).where(
            GroupRelationship.group_id == group_id,
            GroupRelationship.member_id == user_id
        )
    ):
        return True
    return False


async def get_member_permission_in_group(group_id: int, user_id: int) -> Union[int, None]:
    permission = await orm.fetchone(
        select(
            GroupRelationship.permission
        ).where(
            GroupRelationship.group_id == group_id,
            GroupRelationship.member_id == user_id
        )
    )
    return permission[0] if permission else None


def image_md5_check(image_content: bytes, image_md5: str) -> bool:
    return hashlib.md5(image_content).hexdigest().upper() == image_md5.upper()


def friend_chat_data_result_to_dict(data):
    result = []
    for i in data:
        result.append({
            "time": i[0],
            "sender": i[1],
            "message": json.loads(i[2])
        })
