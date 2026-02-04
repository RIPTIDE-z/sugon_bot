import json
import os
from .logger import plugin_logger as logger

def init(file_path: str) -> None:
    """确保 json 文件存在，不存在则创建空对象 {}。"""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)

def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

init("mark_board.json")
init("count.json")
init("config.json")

mark_board: dict = _load_json("mark_board.json")
count_board: dict = _load_json("count.json")
time: dict = _load_json("config.json")

def write_in(ID, point: int) -> None:
    """写入记分板（自动初始化缺失的 ID 记录）。"""
    ID = str(ID)
    mark_board.setdefault(ID, {"point": 0, "times": 0, "name": ID})

    mark_board[ID]["point"] = int(point)
    mark_board[ID]["times"] = int(mark_board[ID].get("times", 0)) + 1

def save() -> None:
    """计分板数据持久化。"""
    _save_json("mark_board.json", mark_board)

def write_in_count(ID, date: str, week: int) -> None:
    """写入打卡时间（自动初始化缺失的 ID 记录）。"""
    ID = str(ID)
    logger.info(f"正在写入打卡时间 date = <green>{date}</green> week = <green>{week}</green>")

    count_board.setdefault(ID, {})
    count_board[ID]["date"] = date
    count_board[ID]["week"] = int(week)

def save_count() -> None:
    """打卡时间持久化。"""
    _save_json("count.json", count_board)
