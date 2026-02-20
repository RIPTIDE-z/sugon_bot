import json
import os

import httpx

from . import access_token_get

members = []
roles = {}


def init(file_path):
    if not os.path.exists(file_path):
        # 如果文件不存在，创建一个新的文件，并写入{}
        with open(file_path, 'w') as file:
            json.dump({}, file)
    pass


def get_roles(guild_id):
    """获取频道内的所有身份组。详情请见qqbot文档"""
    global roles

    Authorization_Headers = access_token_get.init_authorization_headers()

    url = f"https://api.sgroup.qq.com/guilds/{guild_id}/roles"
    response = httpx.get(url, headers=Authorization_Headers)
    roles = response.json()


def get_members(guild_id, roles_id: list):
    """获取对应身份组ID下的所有成员，详情请见qqbot文档"""
    global owners_id
    global members

    Authorization_Headers = access_token_get.init_authorization_headers()

    for i in roles_id:
        url = f"https://api.sgroup.qq.com/guilds/{guild_id}/roles/{i}/members?limit=2"
        response = httpx.get(url, headers=Authorization_Headers)
        members += response.json()["data"]


def role_check(ID):
    """进行身份组检查，即检查该ID的用户是否处于所获取的身份组成员中"""
    global members
    for member in members:
        try:
            member_info = member["user"]
            if member_info["id"] == ID:
                return True
        except KeyError:
            x = 1

    return False


def get_owners_id(name):
    """获取名称为name的身份组的id"""
    for role in roles["roles"]:
        try:
            role_info = role["id"]
            if role["name"] == name:
                role_id = role_info
        except KeyError:
            role_id = 4

    return role_id
