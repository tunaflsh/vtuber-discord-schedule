#!/usr/bin/env python
import argparse
import calendar
import json
import re
from datetime import timedelta

import dateutil.parser
import dateutil.tz
import pyperclip

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
    '\n    "time delimiter": ","'
    "\n}"
    "\n```"
    "\n"
    "\nschedule.txt"
    "\n```"
    "\nFirst stream https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    "\nOffline"
    "\nSecond stream; Third stream, wed 10am EST"
    "\nOffline"
    "\nOffline"
    "\nOffline"
    "\nOffline"
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
    help="json file specifying the format",
    default="schedule.json",
    metavar="json",
    dest="format",
)
arg = parser.parse_args()


url_pattern = re.compile(r"https?://\S+")
tzinfos = {
    "JST": +9,
    "CEST": +2,
    "CET": +1,
    "UTC": -0,
    "GMT": -0,
    "EDT": -4,
    "EST": -5,
    "PDT": -7,
    "PST": -8,
}
tzinfos = {
    tz: dateutil.tz.tzoffset(tz, offset * 3600) for tz, offset in tzinfos.items()
}


with open(arg.format, "r", encoding="utf-8") as f:
    format = json.load(f)

with open(arg.schedule, "r", encoding="utf-8") as f:
    week_schedule = f.read().splitlines()


heading = format["heading"]
date_format = format.get("date format", "%B %d")
standard_time = format.get("standard time", "12am UTC")
offline = format.get("offline", "offline")
live_format = format.get("live format", "<t:{timestamp}> {title}")
url_format = format.get("live url format", live_format)
stream_delim = format.get("stream delimiter", ";")
time_delim = format.get("time delimiter", ",")


standard_time = dateutil.parser.parse(standard_time, tzinfos=tzinfos)
lastday = dateutil.parser.parse("Sun", default=standard_time)


def parse(*args, **kwargs):
    date = dateutil.parser.parse(*args, **kwargs)
    # the parser will select next week if the date is in the past
    if date > lastday:
        date -= timedelta(days=7)
    return date


weekdays = [parse(day.name, default=standard_time) for day in calendar.Day]
# the parser selects the next closest weekday
schedule = [
    heading.format(
        startdate=weekdays[0].strftime(date_format),
        enddate=weekdays[-1].strftime(date_format),
    )
]

for day_schedule, standard_time in zip(week_schedule, weekdays):
    if not day_schedule:
        continue
    if day_schedule == offline:
        schedule.append(f"- {offline}")
        continue
    for stream in day_schedule.split(stream_delim):
        title, *timestamp = stream.split(time_delim, 1)
        timestamp = parse(timestamp[0], tzinfos=tzinfos) if timestamp else standard_time
        timestamp = int(timestamp.timestamp())
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
