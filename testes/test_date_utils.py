from datetime import datetime

from omniutils.date_utils import DateUtils


def test_to_datetime():
    datetime_value = DateUtils.to_datetime(15, "março", 2023)
    assert datetime_value == datetime(2023, 3, 15)
