import os
import csv
from datetime import datetime

# Calender files
_GYM_ICS = os.path.join(os.path.dirname(__file__), '.gym_calendar.ics')
_GYM_CSV = os.path.join(os.path.dirname(__file__), '.classes.csv')


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


def send_calendar_notification(classes_info):
    _write_csv(classes_info)
    _write_ics(classes_info)


def _write_csv(classes_info):
    with open(_GYM_CSV, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(_CSV_HEADERS)
        for class_info in classes_info:
            class_name, class_time, class_id, class_room, class_start, class_end = class_info
            writer.writerow((class_name, class_start, class_end, class_room, class_id, class_time))


def _write_ics(classes_info):
    with open(_GYM_ICS, 'w') as f:
        f.write(f'BEGIN:VCALENDAR\n'
                f'{_TIME_ZONE_SETTINGS}'
                f'{"".join(map(_ics_event, classes_info))}'
                f'END:VCALENDAR')


def _ics_event(class_info):
    class_name, class_time, class_id, class_room, class_start, class_end = class_info
    return f'BEGIN:VEVENT\n' \
           f'DTSTAMP:{datetime.now():_EVENT_DATETIME_FORMAT}\n' \
           f'DTSTART;TZID=Pacific/Auckland:{class_start:_EVENT_DATETIME_FORMAT}' \
           f'DTEND;TZID=Pacific/Auckland:{class_end:_EVENT_DATETIME_FORMAT}\n' \
           f'SUMMARY:{class_name}\n' \
           f'LOCATION:{class_room}\n' \
           f'DESCRIPTION:https://ucrecsportapp/classes/{class_id}/{class_start:%Y%m%d}\n' \
           f'UID:{class_id}\n' \
           f'END:VEVENT\n'
    
