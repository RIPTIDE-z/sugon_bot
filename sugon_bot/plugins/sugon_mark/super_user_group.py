import json
from pathlib import Path

# 固定默认管理员（硬编码），确保基础权限始终可用
DEFAULT_SUPER_USERS = [
    "6EE6FD83223EB85FDFF79452C2F20D2E",
    "8DF759B2BBA2C23964E4E27F58C974CA",
]

# 项目根目录：.../sugon_bot/plugins/sugon_mark/super_user_group.py往上三级
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
SUPER_USER_FILE = DATA_DIR / "super_user_group.json"
LEGACY_SUPER_USER_FILE = PROJECT_ROOT / "super_user_group.json"


def init(file_path: Path):
    # 统一把运行数据放到 data 目录。
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        with file_path.open("w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=2)


def _migrate_legacy_file() -> None:
    # 兼容旧路径：如果根目录下存在旧文件且 data 中还没有，就迁移过去。
    if SUPER_USER_FILE.exists():
        return
    if LEGACY_SUPER_USER_FILE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        LEGACY_SUPER_USER_FILE.replace(SUPER_USER_FILE)


def _load_super_users(file_path: Path) -> list:
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return list(data) if isinstance(data, list) else []


def save():
    with SUPER_USER_FILE.open("w", encoding="utf-8") as f:
        json.dump(super_user_group, f, ensure_ascii=False, indent=2)


_migrate_legacy_file()
init(SUPER_USER_FILE)

super_user_group = _load_super_users(SUPER_USER_FILE)

for fixed_admin in DEFAULT_SUPER_USERS:
    if fixed_admin not in super_user_group:
        super_user_group.append(fixed_admin)

save()


def join_super(ID):
    super_user_group.append(ID)
    save()


def check_super_user_group(ID) -> bool:
    if ID in super_user_group:
        return True
    else:
        return False
