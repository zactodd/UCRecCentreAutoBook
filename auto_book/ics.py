import os
import utils
from datetime import datetime
import re
from booking import FACILITY_ID

# Calender files
_GYM_ICS = os.path.join(os.path.dirname(__file__), '.gym_calendar.ics')
_ICS_EVENT_BLOCK = r'BEGIN:VEVENT((.|\n)*?)END:VEVENT'
_ICS_DSTART = r'DTSTART((;(.*):)|:)(.*?)\n'


_CSV_HEADERS = ('ClassName', 'Start', 'End', 'Location', 'ClassID', 'Date')


_EVENT_DATETIME_FORMAT = '%Y%m%dT%H%M%S'


_TIME_ZONE_SETTINGS = """
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:Pacific/Auckland
LAST-MODIFIED:20201011T015911Z
TZURL:http://tzurl.org/zoneinfo-outlook/Pacific/Auckland
X-LIC-LOCATION:Pacific/Auckland
BEGIN:DAYLIGHT
TZNAME:NZDT
TZOFFSETFROM:+1200
TZOFFSETTO:+1300
DTSTART:19700927T020000
RRULE:FREQ=YEARLY;BYMONTH=9;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZNAME:NZST
TZOFFSETFROM:+1300
TZOFFSETTO:+1200
DTSTART:19700405T030000
RRULE:FREQ=YEARLY;BYMONTH=4;BYDAY=1SU
END:STANDARD
END:VTIMEZONE
""".strip()


def make_ics(classes_info):
    keep_events = []
    if os.path.exists(_GYM_ICS):
        with open(_GYM_ICS, 'r') as f:
            keep_events = _ics_to_keep(f.read())

    with open(_GYM_ICS, 'w') as f:
        f.write(f'BEGIN:VCALENDAR\n{_TIME_ZONE_SETTINGS}\n')
        if keep_events:
            f.write(''.join(keep_events))
        f.write(''.join(map(_ics_event, classes_info)))
        f.write('END:VCALENDAR')


def _ics_event(class_info):
    class_name, class_time, class_id, class_room, class_start, class_end = class_info
    return f'BEGIN:VEVENT\n' \
           f'DTSTAMP:{datetime.now():{_EVENT_DATETIME_FORMAT}}\n' \
           f'DTSTART;TZID=Pacific/Auckland:{class_start:{_EVENT_DATETIME_FORMAT}}\n' \
           f'DTEND;TZID=Pacific/Auckland:{class_end:{_EVENT_DATETIME_FORMAT}}\n' \
           f'SUMMARY:{class_name}\n' \
           f'LOCATION:{class_room}\n' \
           f'DESCRIPTION:https://ucrecsportapp/classes/{FACILITY_ID}/{class_id}/{class_start:%Y%m%d}\n' \
           f'UID:{class_id}\n' \
           f'END:VEVENT\n'


def _ics_to_keep(ics):
    expired = datetime.now() - utils.SEVEN_DAYS
    keep_events = []
    events = re.findall(_ICS_EVENT_BLOCK, ics)
    for e in events:
        e = e[0]
        date_str = re.findall(_ICS_DSTART, e)[0][0]
        if datetime.strptime(date_str, _EVENT_DATETIME_FORMAT) > expired:
            keep_events.append(f'BEGIN:VEVENT{e}END:VCALENDAR\n')
    return keep_events
