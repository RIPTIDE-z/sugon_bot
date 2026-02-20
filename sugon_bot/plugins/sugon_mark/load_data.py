import json
from pathlib import Path

from .logger import plugin_logger as logger

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"

MARK_BOARD_FILE = DATA_DIR / "mark_board.json"
COUNT_FILE = DATA_DIR / "count.json"
CONFIG_FILE = DATA_DIR / "config.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def init(file_path: Path) -> None:
    """确保 json 文件存在，不存在则创建空对象 {}。"""
    _ensure_data_dir()
    if not file_path.exists():
        with file_path.open("w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


init(MARK_BOARD_FILE)
init(COUNT_FILE)
init(CONFIG_FILE)

mark_board: dict = _load_json(MARK_BOARD_FILE)
count_board: dict = _load_json(COUNT_FILE)
time: dict = _load_json(CONFIG_FILE)


def write_in(ID, point: int) -> None:
    """写入记分板（自动初始化缺失的 ID 记录）。"""
    ID = str(ID)
    mark_board.setdefault(ID, {"point": 0, "times": 0, "name": ID})

    mark_board[ID]["point"] = int(point)
    mark_board[ID]["times"] = int(mark_board[ID].get("times", 0)) + 1


def save() -> None:
    """计分板数据持久化。"""
    _save_json(MARK_BOARD_FILE, mark_board)


def write_in_count(ID, date: str, week: int) -> None:
    """写入打卡时间（自动初始化缺失的 ID 记录）。"""
    ID = str(ID)
    logger.info(f"正在写入打卡时间 date = <green>{date}</green> week = <green>{week}</green>")

    count_board.setdefault(ID, {})
    count_board[ID]["date"] = date
    count_board[ID]["week"] = int(week)


def save_count() -> None:
    """打卡时间持久化。"""
    _save_json(COUNT_FILE, count_board)
