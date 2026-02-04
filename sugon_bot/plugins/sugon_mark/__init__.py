from pathlib import Path
from typing import Type
import datetime
import re
from . import group_image_check

import nonebot
from nonebot import get_driver, Bot
from nonebot.adapters.qq import Event, GuildMessageEvent, GroupRobotEvent
from nonebot.internal.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import RawCommand, CommandArg
from nonebot.adapters import Message
from nonebot.permission import SUPERUSER

from .config import Config
from . import load_data
from . import link_check
from .guild_api import get_roles, get_members, role_check, get_owners_id
from .time_check import TimeCheckPlugin
from .mark_caculate import MarkCalculate
from . import super_user_group

from .logger import plugin_logger as logger

time_checker = TimeCheckPlugin()
MarkCalculate = MarkCalculate()

__plugin_meta__ = PluginMetadata(
    name="sugon-mark",
    description="",
    usage="",
    config=Config,
)

global_config = get_driver().config
config = Config.parse_obj(global_config)

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

def _has_space_after_cmd(full_text: str, raw_cmd: str) -> bool:
    """判断 raw_cmd 后面是否紧跟空白符（空格/制表/换行等）"""
    if not full_text.startswith(raw_cmd):
        return True
    tail = full_text[len(raw_cmd):]
    return bool(tail) and tail[0].isspace()

async def require_text_arg(
    *,
    event: Event,
    matcher: Type[Matcher],
    raw_cmd: str,
    arg_text: str,
    usage: str,
    arg_name: str = "参数",
) -> None:
    """要求必须有参数；并区分：缺空格 vs 缺参数"""
    full = event.get_plaintext()
    has_space = _has_space_after_cmd(full, raw_cmd)

    # 有参数但没空格：/NAME张三
    if arg_text and not has_space:
        await matcher.finish(f"指令与{arg_name}之间需要空格哦🥺\n用法：{usage}")

    # 没参数：/NAME 或 /NAME<空格>
    if not arg_text:
        await matcher.finish(f"缺少{arg_name}哦🥺\n用法：{usage}")

async def name_check(ID, matcher: Type[Matcher]):
    """这是一个命名检查，如果没有设置称呼，则输出提示。"""
    ID = str(ID)
    obj = load_data.mark_board.get(ID)
    if obj is None:
        await matcher.finish("请先设置你的姓名：/NAME 张三")
    return obj


async def image_check(matcher: Type[Matcher], event: Event, object):
    """这是一个图片检查，检查整个消息序列中是否有图片。如果没有，输出提示"""

    args = event.get_message()

    for segment in args:
        if segment.type != "image":
            continue

        url = segment.data.get("url", "")
        if url and (link_check.is_image_url(url) or group_image_check.is_image_url(url)):
            return True

        # 有 image 段但不是合法截图
        await matcher.finish("你这家伙，这可不是截图ε=( o｀ω′)ノ")

    # 循环结束都没找到图片
    return False


async def point_calculate(is_legal, ID, matcher: Type[Matcher], point):
    """打卡检查：合法 + 未重复 + 在允许时间段内 -> 记一次打卡并更新积分。"""
    if not is_legal:
        await matcher.finish("你的打卡内容呢？")

    ID = str(ID)

    # 限制只能在 start/end 时间段内打卡
    if not time_checker.time_check():
        logger.info(f"不在打卡时间段")
        await matcher.finish("现在不在打卡时间段内哦 _(:3 ⌒ﾞ)_")

    today = time_checker.now_time

    # 区分：没有打卡记录 vs 重复打卡
    rec = load_data.count_board.get(ID)
    if rec is None:
        logger.info(f"用户 <green>{ID}</green> 没有签到记录")
    else:
        last_date = rec.get("date")
        if last_date == today:
            logger.info(f"用户 <green>{ID}</green> 今天已经签到过了")
            await matcher.finish("你今天已经签到过了哦！ε=( o｀ω′)ノ")

    logger.info(f"用户 <green>{ID}</green> 今天还没有签到")
    # 通过：写入本次打卡时间
    load_data.write_in_count(ID, today, int(time_checker.get_week()))
    load_data.save_count()

    # TODO:打卡次数检查相关
    #times_check(ID, time_checker.now_time_date)

    # 更新积分
    old_point = int(load_data.mark_board.get(ID, {}).get("point", 0))
    delta = MarkCalculate.calculate(point, ID)
    new_point = old_point + delta

    load_data.write_in(ID, new_point)
    load_data.save()

    name = load_data.mark_board.get(ID, {}).get("name", ID)
    await matcher.finish(f"{name}打卡成功!")

@name.handle()
async def name_handle(
    event: Event,
    raw_cmd: str = RawCommand(),
    arg_msg: Message = CommandArg(),
):
    ID = str(event.get_user_id())
    arg_text = arg_msg.extract_plain_text().strip()

    await require_text_arg(
        event=event,
        matcher=name,
        raw_cmd=raw_cmd,
        arg_text=arg_text,
        usage="/NAME 张三",
        arg_name="姓名",
    )

    # 写入
    load_data.mark_board.setdefault(ID, {"point": 0, "name": arg_text, "times": 0})
    load_data.mark_board[ID]["name"] = arg_text
    load_data.save()

    await name.finish("好的，那么我将称呼你为" + arg_text)

# TODO:重写note逻辑
@mark_note.handle()
async def mark_note_handle(
    event: Event,
    raw_cmd: str = RawCommand(),
    arg_msg: Message = CommandArg(),
):
    ID = str(event.get_user_id())
    await name_check(ID, matcher=mark_note)

    # 检查是否带截图
    has_image = any(seg.type == "image" for seg in arg_msg)

    # 没图 -> 需要文本参数和链接
    arg_text = arg_msg.extract_plain_text().strip()
    if not has_image:
        await require_text_arg(
            event=event,
            matcher=mark_note,
            raw_cmd=raw_cmd,
            arg_text=arg_text,
            usage="/note [发送截图] 或 /note <截图链接>",
            arg_name="截图链接",
        )
        # 可选：强制要求是链接（否则用户随便打字也会过）
        if not re.search(r"https?://\S+", arg_text):
            await mark_note.finish("请提供截图链接（以 http:// 或 https:// 开头）")

    # 3) 合法性检查：你现有 image_check 只查图片 segment。
    #    如果你也要支持“纯链接”，那就需要在这里额外检查 arg_text 是否为合法图片链接。
    #    不想改 image_check 的话，就在这里补一段：
    is_legal = await image_check(matcher=mark_note, event=event, object=None)
    if (not is_legal) and (not has_image) and arg_text:
        # 链接校验（复用你已有的两个链接判断）
        if link_check.is_image_url(arg_text) or group_image_check.is_image_url(arg_text):
            is_legal = True

    await point_calculate(is_legal, ID, mark_note, 1)

@mark_normal.handle()
async def mark_normal_handle(
    event: Event,
    raw_cmd: str = RawCommand(),
    arg_msg: Message = CommandArg(),
):
    logger.info("检测到截图打卡事件")

    ID = str(event.get_user_id())
    logger.info(f"打卡者ID为 <green>{ID}</green>")

    await name_check(ID, matcher=mark_normal)

    full = event.get_plaintext()
    arg_text = arg_msg.extract_plain_text().strip()

    # 文本描述检查
    await require_text_arg(
        event=event,
        matcher=mark_normal,
        raw_cmd=raw_cmd,
        arg_text=arg_text,
        usage="/normal[空格]笔记描述[空格][图片]",
        arg_name="笔记描述",
    )

    # 图片检查
    has_image = any(seg.type == "image" for seg in event.get_message())
    if not has_image:
        await mark_normal.finish("缺少笔记截图哦🥺\n用法：/normal[空格]笔记描述[空格][图片]")

    # 校验图片是否为合法截图
    is_legal = await image_check(matcher=mark_normal, event=event, object=None)

    await point_calculate(is_legal, ID, mark_normal, 1)

@show_all.handle()
async def handle_show_all(bot: Bot, event: Event, Guild_event: GuildMessageEvent):
    """这是显示所有人的积分的事件响应处理"""

    id = Guild_event.guild_id
    get_roles(id)
    id_list = [get_owners_id("频道主"), get_owners_id("超级管理员")]
    get_members(id, id_list)
    ID = event.get_user_id()

    if not super_user_group.check_super_user_group(ID) :
        await show_all.finish("你没有权限执行这个操作！")

    if load_data.mark_board == {}:
        await show_all.finish("看来还没有人打卡的样子，真是冷清QAQ")

    logger.info("正在输出积分榜")

    # 排序：积分降序
    records = sorted(
        load_data.mark_board.values(),
        key=lambda x: (-int(x.get("point", 0)), str(x.get("name", ""))),
    )

    lines = [f"{item.get('name', '未知')}：{int(item.get('point', 0))} 分" for item in records]
    msg = "好的，管理员，积分榜如下：\n" + "\n".join(lines)
    await show_all.finish(msg)

@show_all.handle()
async def group_show_all(bot: Bot,event:Event):
    """这是显示所有人的积分的事件响应处理"""
    ID = event.get_user_id()
    if not super_user_group.check_super_user_group(ID) :
        await show_all.finish("你没有权限执行这个操作！")

    if load_data.mark_board == {}:
        await show_all.finish("看来还没有人打卡的样子，真是冷清QAQ")

    logger.info("正在输出积分榜", "green")

    # 排序：积分降序
    records = sorted(
        load_data.mark_board.values(),
        key=lambda x: (-int(x.get("point", 0)), str(x.get("name", ""))),
    )

    lines = [f"{item.get('name', '未知')}：{int(item.get('point', 0))} 分" for item in records]
    msg = "好的，管理员，积分榜如下：\n" + "\n".join(lines)
    await show_all.finish(msg)

@remove.handle()
async def remove_mark(
    event: Event,
    raw_cmd: str = RawCommand(),
    arg_msg: Message = CommandArg(),
):
    ID = str(event.get_user_id())
    if not super_user_group.check_super_user_group(ID):
        await remove.finish("你没有权限执行这个操作！")

    target_name = arg_msg.extract_plain_text().strip()

    await require_text_arg(
        event=event,
        matcher=remove,
        raw_cmd=raw_cmd,
        arg_text=target_name,
        usage="/remove 张三",
        arg_name="姓名",
    )

    keys_to_delete = [k for k, v in load_data.mark_board.items() if v.get("name") == target_name]
    for k in keys_to_delete:
        load_data.mark_board.pop(k, None)
    load_data.save()

    await remove.finish("已经删除" + target_name + "的积分信息！")

@set_score.handle()
async def handle_set_score(
    event: Event,
    raw_cmd: str = RawCommand(),
    arg_msg: Message = CommandArg(),
):
    ID = str(event.get_user_id())
    if not super_user_group.check_super_user_group(ID):
        await set_score.finish("你没有权限执行这个操作！")

    text = arg_msg.extract_plain_text().strip()
    full = event.get_plaintext()
    if text and not _has_space_after_cmd(full, raw_cmd):
        await set_score.finish("指令与参数之间需要空格。\n用法：/setscore 张三 10")

    parts = text.split()
    if len(parts) < 2:
        await set_score.finish("缺少参数。\n用法：/setscore 张三 10")

    target_name, score_str = parts[0], parts[1]
    try:
        score = float(score_str)
    except ValueError:
        await set_score.finish("分数必须是数字。\n用法：/setscore 张三 10")

    for _, value in load_data.mark_board.items():
        if value.get("name") == target_name:
            value["point"] = score
    load_data.save()

    await set_score.finish(f"已经修改{target_name}的积分为 {score}！")

@set_super_user.handle()
async def handle_set_super_user(
    event: Event,
    raw_cmd: str = RawCommand(),
    arg_msg: Message = CommandArg(),
):
    ID = str(event.get_user_id())
    if not super_user_group.check_super_user_group(ID):
        await set_super_user.finish("你没有权限执行这个操作！")

    target_id = arg_msg.extract_plain_text().strip()

    await require_text_arg(
        event=event,
        matcher=set_super_user,
        raw_cmd=raw_cmd,
        arg_text=target_id,
        usage="/super 123456",
        arg_name="目标ID",
    )

    if super_user_group.check_super_user_group(target_id):
        await set_super_user.finish("这位用户已经是管理员了。")

    super_user_group.join_super(target_id)
    await set_super_user.finish("已经将ID为" + target_id + "的用户设为管理员")
