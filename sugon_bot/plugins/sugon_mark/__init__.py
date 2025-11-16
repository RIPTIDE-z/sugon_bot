from pathlib import Path
from typing import Type
import datetime
import re
from . import group_image_check

import nonebot
from nonebot import get_plugin_config
from nonebot import get_driver, Bot
from nonebot.adapters.qq import Event, GuildMessageEvent, GroupRobotEvent
from nonebot.internal.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.permission import SUPERUSER

from .config import Config
from . import load_data
from . import link_check
from .guild_api import get_roles, get_members, role_check, get_owners_id
from .time_check import TimeCheckPlugin
from .mark_caculate import MarkCalculate
from . import super_user_group


TimeCheckPlugin = TimeCheckPlugin()
MarkCalculate = MarkCalculate()

__plugin_meta__ = PluginMetadata(
    name="sugon-mark",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

sub_plugins = nonebot.load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)

# 定义事件响应
mark_note = on_command("marknote", aliases={"marknote", "note", "笔记打卡"}, priority=10, block=True)
mark_normal = on_command("marknormal", aliases={"marknormal", "normal", "截图打卡"}, priority=10, block=True)
name = on_command("nn", aliases={"nn", "NAME", "请叫我"}, priority=10, block=True)
show_all = on_command("show", aliases={"show"}, priority=10, block=True)
remove = on_command("remove", aliases={"remove"},priority=10,block=True)
set_score = on_command("setscore", aliases={"setscore"},priority=10,block=True)
get_user_id =on_command("get_user_id",aliases={"ID"},priority=10,block=True)
set_super_user =on_command("set_super_user",aliases={"super"},priority=10,block=True)

def times_check(ID, date):
    """这是一个打卡次数的检查。"""
    if MarkCalculate.check_week(ID, date):
        load_data.mark_board[ID]["times"] = 0
        return True
    if load_data.mark_board[ID]["times"] < 5:
        return True
    else:
        return False


async def command_check(event: Event,matcher: Type[Matcher],index:int):
    args = event.get_plaintext()
    ID = event.get_user_id()
    if args[index] != " ":
        await matcher.finish("指令的格式不正确哦！")


async def name_check(ID, matcher: Type[Matcher]):
    """这是一个命名检查，如果没有设置称呼，则输出提示。"""
    try:

        object = load_data.mark_board[ID]

    except KeyError:

        await matcher.finish("请先设置你的姓名：/NAME [name]")

    return object


async def image_check(matcher: Type[Matcher], event: Event, object):
    """这是一个图片检查，检查整个消息序列中是否有图片。如果没有，输出提示"""

    is_in_time = TimeCheckPlugin.time_check()

    if not is_in_time:
        await matcher.finish(object["name"] + "现在不在打卡时间哦")

    args = event.get_message()

    is_image = False
    is_legal = False

    for segment in args:  # 遍历消息中的每个片段
        if segment.type == 'image':
            if link_check.is_image_url(segment.data['url']):
                is_image = True
                is_legal = True
                print(link_check.is_image_url(segment.data['url']))
                break
            elif group_image_check.is_image_url(segment.data['url']):
                print(group_image_check.is_image_url(segment.data['url']))
                is_image =True
                is_legal = True
                break

            if not is_image:
                await matcher.finish("你这家伙，这可不是截图ε=( o｀ω′)ノ")

                pass

    return is_legal


async def point_calculate(is_legal, ID, matcher: Type[Matcher], point):
    """这是一个打卡检查，如果打卡内容合法，而且今天还没有签到，则进行打卡。"""
    is_marked = False
    if is_legal:

        try:

            pastime = load_data.count_board[ID]["date"]

            if TimeCheckPlugin.date_check(pastime):
                is_marked = True
                await matcher.finish("你今天已经签到过了哦！ε=( o｀ω′)ノ")

        except Exception as e:

            TimeCheckPlugin.time_solve()
            load_data.count_board[ID] = {"date": TimeCheckPlugin.now_time, "week": TimeCheckPlugin.now_time_date}

        if is_marked:
            return

        times_check(ID, TimeCheckPlugin.now_time_date)

        load_data.write_in_count(ID, TimeCheckPlugin.now_time, int(TimeCheckPlugin.get_week()))
        load_data.save_count()

        try:
            point = int(load_data.mark_board[ID]["point"]) + MarkCalculate.calculate(point, ID)

        except KeyError:

            load_data.mark_board[ID]["point"] = MarkCalculate.calculate(point, ID)

            point = load_data.mark_board[ID]["point"]

        load_data.write_in(ID, point)
        load_data.save()

        await matcher.finish(load_data.mark_board[ID]["name"] + "打卡成功!")
    else:

        await matcher.finish("你的打卡内容呢？")


@name.handle()
async def name_handle(event: Event):
    """这是进行命名的事件响应处理"""
    # TODO：应该检查该指令的变量，即名称是否合法，例如是否是纯文本
    args = event.get_plaintext()
    ID = event.get_user_id()
    await command_check(event=event,matcher=name,index=5)

    try:

        load_data.mark_board[ID]["name"] = args[6:]

    except KeyError:

        load_data.mark_board[ID] = {"point": 0, "name": args[6:], "times": 0}

    load_data.save()

    await name.finish("好的，那么我将称呼你为" + args[6:])

    pass


@mark_note.handle()
async def mark_note_handle(event: Event):
    """这是笔记打卡的事件响应处理"""

    ID = event.get_user_id()

    object = await name_check(ID, matcher=mark_note)

    await command_check(event=event, matcher=name,index=5)

    is_legal = await image_check(matcher=mark_note, event=event, object=object)

    await point_calculate(is_legal, ID, mark_note, 1)

    pass


@mark_normal.handle()
async def mark_normal_handle(event: Event):
    """这是截图打卡的事件响应处理"""

    ID = event.get_user_id()

    object = await name_check(ID, matcher=mark_normal)

    await command_check(event=event, matcher=name,index=7)

    is_legal = await image_check(matcher=mark_normal, event=event, object=object)

    await point_calculate(is_legal, ID, mark_normal, 1)

    pass


@show_all.handle()
async def handle_show_all(bot: Bot, event: Event, Guild_event: GuildMessageEvent):
    """这是显示所有人的积分的事件响应处理"""

    id = Guild_event.guild_id
    get_roles(id)
    id_list = [get_owners_id("频道主"), get_owners_id("超级管理员")]
    get_members(id, id_list)
    ID = event.get_user_id()

    if not role_check(ID):
        await show_all.send("你没有权限执行这个操作！")
        return 0
    else:
        await show_all.send("好的，管理员，以下是所有的积分")
    ans = ""
    if load_data.mark_board == {}:
        await show_all.finish("看来还没有人打卡的样子，真是冷清QAQ")
    for item in load_data.mark_board.values():
        ans = ans + item["name"] + "积分:" + str(item["point"]) + "\n"
    await show_all.finish(ans)

@show_all.handle()
async def group_show_all(bot: Bot,event:Event):
    """这是显示所有人的积分的事件响应处理"""
    ID = event.get_user_id()
    if super_user_group.check_super_user_group(ID):
        await show_all.send("好的，管理员，以下是所有的积分")
    else:
        await show_all.send("你没有权限执行这个操作！")
        return 0
    ans = ""
    if load_data.mark_board == {}:
        await show_all.finish("看来还没有人打卡的样子，真是冷清QAQ")
    for item in load_data.mark_board.values():
        ans = ans + item["name"] + "积分:" + str(item["point"]) + "\n"
    await show_all.finish(ans)

@remove.handle()
async def remove_mark(bot: Bot,event:Event):

    ID = event.get_user_id()
    if super_user_group.check_super_user_group(ID):
        await remove.send("好的，管理员，为您进行操作")
    else:
        await remove.send("你没有权限执行这个操作！")
        return 0
    args = event.get_plaintext()
    pattern = r"/remove\s+(.*)"
    match = re.search(pattern, args)
    keys_to_delete = [key for key, value in load_data.mark_board.items() if value["name"] == match.group(1)]
    for item in keys_to_delete:
        load_data.mark_board.pop(item)
        load_data.save()
    await remove.finish("已经删除"+match.group(1)+"的积分信息！")

@set_score.handle()
async def handle_set_score(bot: Bot,event:Event):
    ID = event.get_user_id()
    if super_user_group.check_super_user_group(ID):
        await set_score.send("好的，管理员，为您进行操作")
    else:
        await set_score.send("你没有权限执行这个操作！")
        return 0
    args = event.get_plaintext()
    pattern = r"/setscore\s+(\S+)\s+([\d\.]+)"

    # 执行匹配
    match = re.search(pattern, args)
    score = float()
    name = ''
    if match:
        name = match.group(1)  # 获取第一个捕获组 (name)
        score = float(match.group(2))  # 获取第二个捕获组 (score) 并转换为浮动数
    else:
        print("没有匹配到")
    for key, value in load_data.mark_board.items():
        if value["name"] == name:
            value["point"] = score  # 修改 point 为新的 score
            load_data.save()
    await set_score.finish("已经修改"+match.group(1)+"的积分！")

@get_user_id.handle()
async def handle_get_user_id(bot:Bot,event:Event):
    ID = event.get_user_id()
    await get_user_id.finish("你的ID是"+ID)

@set_super_user.handle()
async def handle_set_super_user(bot:Bot,event:Event):
    ID = event.get_user_id()
    if super_user_group.check_super_user_group(ID):
        await set_super_user.send("好的，管理员，为您进行操作")
    else:
        await set_super_user.send("你没有权限执行这个操作！")
        return 0
    args = event.get_plaintext()
    pattern = r"/super\s+(.*)"
    match = re.search(pattern, args)
    super_user_id = match.group(1)
    if super_user_group.check_super_user_group(super_user_id):
        await set_super_user.finish("这位用户已经是管理员了。")
        return

    super_user_group.join_super(super_user_id)
    await set_super_user.finish("已经将ID为"+super_user_id+"的用户设为管理员")
