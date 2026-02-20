import datetime
from datetime import timedelta

from . import load_data
from .logger import plugin_logger as logger

class TimeCheckPlugin:
    """
    时间检查与“有效日期”计算。

    - time_check(): 判断当前时间是否处于 start/end 的允许区间内（支持跨午夜）
    - now_time: 有效日期字符串（YYYY-MM-DD）
    - now_time_date: 有效日期对应的 datetime（当天 00:00:00）
    - flag: 跨午夜时用于把凌晨归到前一天（例如 00:30 归前一天 -> flag=-1）
    """

    now_time: str
    now_time_date: datetime.datetime

    def __init__(self):
        # 打卡开始时间
        self.start: datetime.time | None = None
        # 打卡结束时间
        self.end: datetime.time | None = None
        self.flag: int = 0
        self.now: datetime.datetime = datetime.datetime.now()

        self.time_set()
        self.time_solve()  # 初始化 now_time / now_time_date

    def time_set(self) -> None:
        """从 config.json 读取 start/end 时间。"""
        st = load_data.time["start_time"]
        ed = load_data.time["end_time"]
        self.start = datetime.time(st["hour"], st["minute"], st["second"])
        self.end = datetime.time(ed["hour"], ed["minute"], ed["second"])

    def _update_flag_and_now(self) -> bool:
        """
        更新 self.now、self.flag，并返回当前是否在允许时间段内。
        """
        self.now = datetime.datetime.now()
        now_t = self.now.time()

        assert self.start is not None and self.end is not None

        if self.start <= self.end:
            # 不跨午夜
            self.flag = 0
            inside = self.start <= now_t <= self.end
        else:
            # 跨午夜：例如 17:00 - 次日 02:00
            inside = (now_t >= self.start) or (now_t <= self.end)
            self.flag = -1 if now_t <= self.end else 0

        return inside

    def time_check(self) -> bool:
        """判断当前时间是否处于 start/end 之间（支持跨午夜），并刷新 now_time。"""
        inside = self._update_flag_and_now()
        if inside:
            self.time_solve()
        return inside

    def time_solve(self) -> None:
        """
        计算“有效日期”。
        用 timedelta 处理跨月/跨年，避免 day+flag 产生非法日期。
        """
        self.now = datetime.datetime.now()
        d = (self.now + timedelta(days=self.flag)).date()
        self.now_time = d.strftime("%Y-%m-%d")
        self.now_time_date = datetime.datetime.combine(d, datetime.time.min)

    def date_check(self, pass_date: str) -> bool:
        """判断 pass_date 是否等于当前有效日期（YYYY-MM-DD）。"""
        self._update_flag_and_now()  # 保证 flag 最新
        self.time_solve()
        return pass_date == self.now_time

    def get_week(self) -> int:
        """返回 ISO 周数（1-53），不是星期几。"""
        self._update_flag_and_now()
        self.time_solve()
        return self.now_time_date.isocalendar().week
