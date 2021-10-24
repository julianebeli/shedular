"""
time uses arrow module
day = arrow.get(race_day)
race_time = day.shift(hours=h,minutes=m)
race_lead_in = race_time.shift(minutes=-lead_in)
race_lead_out = race_time.shift(minutes=race_duraction).shift(minutes=lead_out)

Python 3.8.3 (tags/v3.8.3:6f8c832, May 13 2020, 22:37:02) [MSC v.1924 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import arrow
>>> s = arrow.get(2021,4,1)
>>> s
<Arrow [2021-04-01T00:00:00+00:00]>
>>> u=arrow.get(2021,1,1)
>>> v = arrow.get(2021,8,1)
>>> v
<Arrow [2021-08-01T00:00:00+00:00]>
>>> u
<Arrow [2021-01-01T00:00:00+00:00]>
>>> u<s<v
True
>>> r = s.shift(minutes=-15)
>>> r
<Arrow [2021-03-31T23:45:00+00:00]>
>>> t=s.shift(minutes=15)
>>> r<s<t
True
>>> t=t.shift(hours=3)
>>> t
<Arrow [2021-04-01T03:15:00+00:00]>
>>> r<s<t
True
>>>

"""

import re
import arrow


def boat_time(race_day, race_start, lead_in, race_time, lead_out):
    # return the time envelope for this boat.
    # in_use_from, in_use_to
    # print(race_day,race_start,lead_in,race_time,lead_out)
    race_lead_in = race_start.shift(minutes=-lead_in)
    race_lead_out = race_start.shift(minutes=race_time).shift(minutes=lead_out)
    # print(race_lead_in)
    # print(race_lead_out)
    return dict(in_use_from=race_lead_in, in_use_until=race_lead_out)


def event_day(s):
    [day, month, year] = list(map(lambda x: int(x), s.split("/")))
    return arrow.get(year, month, day)


def race_start(regatta_day, day, s):
    [(hours, minutes, am)] = re.findall(r"(\d+):(\d+) (\w\w)", s)
    hours = int(hours)
    minutes = int(minutes)
    if am == "PM" and hours < 12:
        hours += 12
    return regatta_day.shift(days=int(day) - 1, hours=hours, minutes=minutes)
