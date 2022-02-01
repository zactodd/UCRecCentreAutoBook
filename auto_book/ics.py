import os
from datetime import datetime
import booking

# ICS file
_GYM_ICS = os.path.join(os.path.dirname(__file__), '.gym_calendar.ics')

# Regex ics
_ICS_EVENT_BLOCK = r'BEGIN:VEVENT((.|\n)*)END:VEVENT'
_ICS_DSTART = r'DTSTART((\;(.*)\:)|\:)(.*)\n'

# Datetime format
_EVENT_DATETIME_FORMAT = '%Y%m%dT%H%M%S'

# ICS Timezone settings
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


def write_ics(username, password, date_from, date_to):
    """
    Write ICS file for classes between dates.
    :param username: The user's username.
    :param password: The user's password.
    :param date_from: The datetime to start from.
    :param date_to: The datetime to end at.
    :return:
    """
    _, token = booking.login(username, password)

    classes = booking.classes_between_dates(date_from, date_to, token)
    with open(_GYM_ICS, 'w') as f:
        f.write(f'BEGIN:VCALENDAR\n{_TIME_ZONE_SETTINGS}\n')
        for c in classes:
            if c.is_booked:
                f.write('BEGIN:VEVENT\n'
                        f'DTSTAMP:{datetime.now():{_EVENT_DATETIME_FORMAT}}\n'
                        f'DTSTART;TZID=Pacific/Auckland:{c.start:{_EVENT_DATETIME_FORMAT}}\n'
                        f'DTEND;TZID=Pacific/Auckland:{c.end:{_EVENT_DATETIME_FORMAT}}\n'
                        f'SUMMARY:{c.name}\n'
                        f'LOCATION:{c.room}\n'
                        f'DESCRIPTION:https://ucrecsportapp/classes/{booking.FACILITY_ID}/{c.id}/{c.start:%Y%m%d}\n'
                        f'UID:{c.id}\n'
                        'END:VEVENT\n')
        f.write('END:VCALENDAR')


def todays_ics(username, password):
    """
    Write ICS file for today classes
    :param username: The user's username.
    :param password: The user's password.
    """
    today = datetime.now()
    write_ics(username, password, today - booking.OPENING_DELTA, today + booking.OPENING_DELTA)

