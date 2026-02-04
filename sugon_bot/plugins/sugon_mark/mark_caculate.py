import datetime
from . import load_data

import holidays
from .logger import plugin_logger as logger

class MarkCalculate:
    """这个类负责进行积分的累进计算。"""

    def __init__(self):
        self.now = datetime.datetime.now()
        self.now_time = str(self.now.year) + str(self.now.month) + str(self.now.day)
        self.china_holidays = holidays.China(years=datetime.date.today().year)

    def calculate(self, mark, ID):
        """这个方法是主要的计算方法。在假日时，积分乘以0.5，如果超出打卡次数，则积分为0"""

        self.now = datetime.datetime.now()
        if self.now in self.china_holidays:
            mark *= 0.5

        if load_data.mark_board[ID]["times"] >= 5:
            mark = 0

        return mark

    def get_weekday(self):
        """"这个方法用于获取当前是周几，返回一个int。"""

        weekdays = datetime.datetime.now().weekday()
        return weekdays

    def check_week(self, ID, date):
        """这个方法用于检测是否在同一周内"""
        week = date.isocalendar().week
        if load_data.count_board[ID]["week"] != week:
            return False
        else:
            return True
