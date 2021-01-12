import re
import datetime

from config import START_DATE, START_TIME, END_TIME, YEAR


class PresentationAssignmentError(Exception):
    def __init__(self, message):
        self.message = message


def time_slot_to_time(time_slot_name):
    # 11:00 am - 12:00 pm
    pattern = r"\s*(\d{1,2}):\d{2}\s*([ap])m\s*"  # Minutes are not captured, but minutes are not assumed to be "00"
    hour, am_pm = re.search(pattern, time_slot_name).group(1, 2)
    hour = int(hour)
    if am_pm == "p":
        hour += 12
    else:
        # TODO: remove assert
        assert am_pm == "a"
    return hour


def column_name_to_date(column_name):
    pattern = r"\[.*?(\w+)\s+([0-3][0-9])\]"
    month, date_ = re.search(pattern, column_name).group(1, 2)
    month = datetime.datetime.strptime(month, "%B").month
    return datetime.date(year=YEAR, month=month, day=int(date_))


def date_and_time_to_index(date_, time_):
    # Assumes that date_ is passed in as a datetime object, time_ is passed in as the hour number (an int)
    start_date = datetime.date.fromisoformat(START_DATE)
    day_num = (date_ - start_date).days
    return (time_ - START_TIME) + day_num * (END_TIME - START_TIME)


def index_to_datetime(index):
    hour = index % (END_TIME - START_TIME) + START_TIME
    minute = int((hour - int(hour)) * 60)
    hour = int(hour)
    date_ = datetime.timedelta(
        days=index // (END_TIME - START_TIME)
    ) + datetime.date.fromisoformat(START_DATE)
    return (
        datetime.datetime(
            year=YEAR, month=date_.month, day=date_.day, hour=hour, minute=minute
        )
        .strftime("%B %d, %Y|%I:%M %p")
        .split("|")
    )


def value_to_excel_csv_string(value):
    return f'"=""{value}""'
