from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from typing import TextIO

from nonebot import logger as nonebot_logger

# 全局开关：True=日志额外写入文件；False=仅保留控制台输出。
ENABLE_FILE_REDIRECT = True
# 日志打印等级
FILE_LOG_LEVEL = "DEBUG"
# 日志文件是否保留颜色信息
FILE_LOG_COLORIZE = False
# 是否采用异步队列记录日志
FILE_LOG_ENQUEUE = False
# 异常回溯是否显示扩展上下文（更深调用链）。False 更简洁
FILE_LOG_BACKTRACE = False
# 异常时是否打印变量诊断信息。True 调试很强，但日志会很长且可能泄露敏感数据
FILE_LOG_DIAGNOSE = False
# 日志格式
FILE_LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {message}"


class HourlyRangeFileSink:
    """
    按小时切分日志文件

    文件名格式：
    log_YYYY_M_D_H_H+1.txt
    例如：log_2026_2_20_18_19.txt
    """

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._current_hour_start: Optional[datetime] = None
        self._file: Optional[TextIO] = None

    @staticmethod
    def _hour_start(dt: datetime) -> datetime:
        return dt.replace(minute=0, second=0, microsecond=0)

    @staticmethod
    def _build_name(hour_start: datetime) -> str:
        hour_end = hour_start + timedelta(hours=1)
        return (
            f"log_{hour_start.year}_{hour_start.month}_{hour_start.day}_"
            f"{hour_start.hour}_{hour_end.hour}.txt"
        )

    def _switch_file(self, record_time: datetime) -> None:
        hour_start = self._hour_start(record_time)
        if self._current_hour_start == hour_start and self._file is not None:
            return

        if self._file is not None:
            self._file.close()

        file_path = self.log_dir / self._build_name(hour_start)
        self._file = file_path.open("a", encoding="utf-8")
        self._current_hour_start = hour_start

    def __call__(self, message) -> None:
        # 使用日志记录时间而不是系统当前时间
        record_time = message.record["time"]
        self._switch_file(record_time)
        assert self._file is not None
        self._file.write(str(message))
        self._file.flush()

    def stop(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None


class PluginLogger:
    """
    插件日志包装器。

    提供带插件前缀的彩色日志输出

    Examples
    --------
    基础使用：

    .. code-block:: python

       from .logger import plugin_logger as logger

       logger.info("这是一条信息")
       logger.success("操作成功")
       logger.warning("这是警告")

    整条消息设置颜色：

    .. code-block:: python

       logger.info("整条消息是绿色", color="green")
       logger.error("整条消息是红色", color="red")

    消息内部使用颜色标签（推荐）：

    .. code-block:: python

       logger.info("用户 <cyan>张三</cyan> 执行了 <green>签到</green> 操作")

       logger.warning("检测到 <red>异常行为</red>，已自动 <yellow>拦截</yellow>")

    Supported Tags
    --------------
    颜色标签：

    - ``<red>...</red>``
    - ``<green>...</green>``
    - ``<yellow>...</yellow>``
    - ``<blue>...</blue>``
    - ``<cyan>...</cyan>``
    - ``<magenta>...</magenta>``

    样式标签：

    - ``<bold>...</bold>``
    - ``<dim>...</dim>``
    - ``<underline>...</underline>``

    """

    _sink_id: Optional[int] = None

    def __init__(self):
        self.logger = nonebot_logger
        self._ensure_file_sink()

    @classmethod
    def _ensure_file_sink(cls) -> None:
        # 通过全局变量决定是否文件重定向
        if not ENABLE_FILE_REDIRECT:
            return

        if cls._sink_id is not None:
            return

        # 统一输出到项目根目录 log/，并按小时切分文件。
        project_root = Path(__file__).resolve().parents[3]
        log_dir = project_root / "log"
        hourly_sink = HourlyRangeFileSink(log_dir)

        cls._sink_id = nonebot_logger.add(
            hourly_sink,
            level=FILE_LOG_LEVEL,
            # 写入文件时不保留颜色
            colorize=FILE_LOG_COLORIZE,
            enqueue=FILE_LOG_ENQUEUE,
            backtrace=FILE_LOG_BACKTRACE,
            diagnose=FILE_LOG_DIAGNOSE,
            format=FILE_LOG_FORMAT,
        )

    @staticmethod
    def _format_msg(msg: str, color: Optional[str] = None) -> str:
        if color:
            return f"<{color}>{msg}</{color}>"
        return msg

    def trace(self, msg: str, color: Optional[str] = None) -> None:
        self.logger.opt(colors=True).trace(self._format_msg(msg, color))

    def debug(self, msg: str, color: Optional[str] = None) -> None:
        self.logger.opt(colors=True).debug(self._format_msg(msg, color))

    def info(self, msg: str, color: Optional[str] = None) -> None:
        self.logger.opt(colors=True).info(self._format_msg(msg, color))

    def success(self, msg: str, color: Optional[str] = None) -> None:
        self.logger.opt(colors=True).success(self._format_msg(msg, color))

    def warning(self, msg: str, color: Optional[str] = None) -> None:
        self.logger.opt(colors=True).warning(self._format_msg(msg, color))

    def error(self, msg: str, color: Optional[str] = None) -> None:
        self.logger.opt(colors=True).error(self._format_msg(msg, color))

    def critical(self, msg: str, color: Optional[str] = None) -> None:
        self.logger.opt(colors=True).critical(self._format_msg(msg, color))


plugin_logger = PluginLogger()
