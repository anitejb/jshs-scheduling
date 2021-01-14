import re
import datetime

from config import (
    JUDGE_AVAILABILITY_DATE_NAME_FORMAT,
    JUDGE_AVAILABILITY_QUESTION_FORMAT,
    JUDGE_AVAILABILITY_TIME_SLOT_FORMAT,
    START_DATE,
    START_TIME,
    END_TIME,
    YEAR,
)


class PresentationAssignmentError(Exception):
    def __init__(self, message):
        self.message = message


class OutputVerificationError(Exception):
    def __init__(self, message):
        self.message = message


def time_slot_to_time(time_slot_name):
    # 11:00 am - 12:00 pm
    pattern = r"\s*(\d{1,2}):\d{2}\s*([ap])m\s*"  # Minutes are not captured, but minutes are not assumed to be "00"
    hour, am_pm = re.search(pattern, time_slot_name).group(1, 2)
    hour = int(hour)
    if am_pm == "p":
        if hour != 12:
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
    return datetime.datetime(
        year=YEAR, month=date_.month, day=date_.day, hour=hour, minute=minute
    )


def index_to_datetime_str(index):
    return index_to_datetime(index).strftime("%B %d, %Y|%I:%M %p").split("|")


def get_column_name_from_datetime(dt):
    dt_format = JUDGE_AVAILABILITY_DATE_NAME_FORMAT.format(
        **{"Weekday": "%A", "Month": "%B", "Date": str(dt.day)}
    )
    dt_str = datetime.datetime.strftime(dt, dt_format)
    return JUDGE_AVAILABILITY_QUESTION_FORMAT.format(**{"date_name": dt_str})


def get_time_slot_availability_string_from_datetime(dt):
    hour = dt.hour - 12 if dt.hour > 12 else dt.hour
    hour_plus_1 = dt.hour + 1 - 12 if dt.hour + 1 > 12 else dt.hour + 1
    am_or_pm_lower = ("p" if 12 <= dt.hour < 24 else "a") + "m"
    plus_1_am_or_pm_lower = ("p" if 12 <= (dt.hour + 1) < 24 else "a") + "m"
    am_or_pm_upper = am_or_pm_lower.upper()
    plus_1_am_or_pm_upper = plus_1_am_or_pm_lower.upper()
    time_slot_str = JUDGE_AVAILABILITY_TIME_SLOT_FORMAT.format(
        **{
            "Hour": hour,
            "AM_or_PM": am_or_pm_upper,
            "am_or_pm": am_or_pm_lower,
            "Hour_Plus_1": hour_plus_1,
            "Plus_1_AM_or_PM": plus_1_am_or_pm_upper,
            "Plus_1_am_or_pm": plus_1_am_or_pm_lower,
        }
    )
    return time_slot_str


def value_to_excel_csv_string(value):
    return f'"=""{value}""'
