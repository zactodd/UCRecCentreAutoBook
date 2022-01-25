import os
from datetime import datetime



_GYM_ICS = CLASSES_TO_BOOK = os.path.join(os.path.dirname(__file__), 'gym_calendar.ics')

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
    pass


def _write_ics(classes_info):
    with open(_GYM_ICS, 'w') as f:
        f.write('BEGIN:VCALENDAR\n')
        f.write(_TIME_ZONE_SETTINGS)
        f.write('\n'.join(map(_ics_event, classes_info)))
        f.write('\nEND:VCALENDAR')


def _ics_event(class_info):
    """
    Generates the ics event str for a given class info.
    :param class_info:
    :return:
    """
    class_name, class_time, class_id, class_room, class_start, class_end = class_info
    return f"""
    BEGIN:VEVENT
    DTSTAMP:{datetime.now():'%Y%m%dT%H%M%SZ'}
    DTSTART;TZID=Pacific/Auckland:{class_start}
    DTEND;TZID=Pacific/Auckland:{class_end}
    SUMMARY:{class_name}
    LOCATION:{class_room}
    DESCRIPTION:https://ucrecsportapp/classes/{class_id}/{}
    UID:{class_id}
    END:VEVENT
    """.strip()
    
