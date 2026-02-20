import datetime

from . import load_data


class MarkCalculate:
    """这个类负责进行积分的累进计算"""

    def calculate(self, mark, _ID):
        """直接返回本次基础积分。"""
        # TODO: 节假日积分计算
        return mark

    def get_weekday(self):
        """"这个方法用于获取当前是周几，返回一个int"""
        weekdays = datetime.datetime.now().weekday()
        return weekdays

    def check_week(self, ID, date):
        """这个方法用于检测是否在同一周内"""
        week = date.isocalendar().week
        if load_data.count_board[ID]["week"] != week:
            return False
        else:
            return True
