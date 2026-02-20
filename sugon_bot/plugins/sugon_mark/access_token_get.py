import nonebot
import requests

config = nonebot.get_driver().config

access_token = ' '

secret = config.qq_bots[0]["secret"]
appId = config.qq_bots[0]["id"]


def job():
    url = 'https://bots.qq.com/app/getAppAccessToken'
    headers = {'Content-Type': 'application/json'}
    data = {
        "appId": {appId},
        "clientSecret": {secret}
    }
    response = requests.post(url, headers=headers, json=data)
    token = response.json()['access_token']
    return token


def get_access_token():
    global access_token
    access_token = job()


def init_authorization_headers():
    get_access_token()

    Authorization_Headers = {
        "Authorization": " ",
        "X-Union-Appid": "102080600"
    }

    Authorization_Headers["Authorization"] = f"QQBot {access_token}"

    return Authorization_Headers
