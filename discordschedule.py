#!/usr/bin/env python
import argparse
import json
import re

import pyperclip
from dateutil.parser import parse as dateparse
from dateutil.relativedelta import MO
from dateutil.relativedelta import relativedelta as delta

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Create a Discord formatted schedule.",
    epilog="Example:"
    "\n"
    "\nschedule.json"
    "\n```"
    "\n{"
    '\n    "heading": "### {startdate} - {enddate}",'
    '\n    "date format": "%B %d",'
    '\n    "standard time": "8pm JST",'
    '\n    "offline": "Offline",'
    '\n    "live format": "- <t:{timestamp}:d> <t:{timestamp}:t> {title}",'
    '\n    "live url format": "- <t:{timestamp}:d> <t:{timestamp}:t> [{title}](<{url}>)",'
    '\n    "stream delimiter": ";",'
    '\n    "time delimiter": ",",'
    '\n    "timezones": {'
    '\n        "EST": -5'
    "\n    }"
    "\n}"
    "\n```"
    "\n"
    "\nschedule.txt"
    "\n```"
    "\nFirst stream https://www.youtube.com/watch?v=dQw4w9WgXcQ # Monday"
    "\nOffline                                                  # Tuesday"
    "\nSecond stream; Third stream, wed 10am EST                # Wednesday"
    "\nOffline                                                  # Thursday"
    "\nOffline                                                  # Friday"
    "\nOffline                                                  # Saturday"
    "\nOffline                                                  # Sunday"
    "\n```"
    "\n"
    "\ndiscordschedule.py schedule.txt -f schedule.json"
    "\n```"
    "\n### December 11 - December 17"
    "\n- <t:1702292400:d> <t:1702292400:t> [First stream](<https://www.youtube.com/watch?v=dQw4w9WgXcQ>)"
    "\n- Offline"
    "\n- <t:1702465200:d> <t:1702465200:t> Second stream"
    "\n- <t:1702479600:d> <t:1702479600:t> Third stream"
    "\n- Offline"
    "\n- Offline"
    "\n- Offline"
    "\n- Offline"
    "\n```",
)
parser.add_argument("schedule", help="text file containing the schedule", metavar="txt")
parser.add_argument(
    "-f",
    "--format",
    help="json file specifying the format. default: schedule.json",
    default="schedule.json",
    metavar="json",
    dest="format",
)
parser.add_argument(
    "-nw",
    "--next-week",
    help="set the schedule to the next Nth weeks. default: 1",
    type=int,
    nargs="?",
    default=0,
    const=1,
    metavar="N",
)
arg = parser.parse_args()

with open(arg.format, "r", encoding="utf-8") as f:
    format = json.load(f)

with open(arg.schedule, "r", encoding="utf-8") as f:
    week_schedule = f.read().splitlines()
    week_schedule = [line.split("#", 1)[0].strip() for line in week_schedule]


heading = format["heading"]
date_format = format.get("date format", "%B %d")
std_time = format.get("standard time", "12am UTC")
offline = format.get("offline", "offline")
live_format = format.get("live format", "<t:{timestamp}> {title}")
url_format = format.get("live url format", live_format)
stream_delim = format.get("stream delimiter", ";")
time_delim = format.get("time delimiter", ",")
tzinfos = {tz: offset * 3600 for tz, offset in format.get("timezones", {}).items()}

url_pattern = re.compile(r"https?://\S+")

# monday of this(+arg.next_week) week
mo = dateparse(std_time, tzinfos=tzinfos) + delta(weeks=arg.next_week, weekday=MO(-1))
mo, *_, su = weekdays = [mo + delta(weekday=i) for i in range(7)]

schedule = [
    heading.format(
        startdate=mo.strftime(date_format),
        enddate=su.strftime(date_format),
    )
]

for day_schedule, std_schedule in zip(week_schedule, weekdays):
    if not day_schedule:
        continue
    if day_schedule == offline:
        schedule.append(f"- {offline}")
        continue
    for stream in day_schedule.split(stream_delim):
        title, *timestamp = stream.split(time_delim, 1)
        timestamp = int(
            (
                dateparse(timestamp[0], tzinfos=tzinfos, default=std_schedule)
                if timestamp
                else std_schedule
            ).timestamp()
        )
        if match := url_pattern.search(title):
            url = match.group()
            title = title[: match.start()].strip() + title[match.end() :]
            schedule.append(
                url_format.format(title=title.strip(), url=url, timestamp=timestamp)
            )
            continue
        schedule.append(live_format.format(title=title.strip(), timestamp=timestamp))

schedule = "\n".join(schedule)
pyperclip.copy(schedule)
print(schedule)
