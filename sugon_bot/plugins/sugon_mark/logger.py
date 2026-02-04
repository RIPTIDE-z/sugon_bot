from nonebot import logger as nonebot_logger
from typing import Optional


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

    def __init__(self):
        self.logger = nonebot_logger

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
