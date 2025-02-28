from datetime import datetime
from omniutils.date_utils import DateUtils

def test_to_datetime():
    dt = DateUtils.to_datetime(15, "março", 2023)
    assert dt == datetime(2023, 3, 15)
