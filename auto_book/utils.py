import requests
import datetime
import json


FACILITY_ID = 'dbf12cf8-3674-4daf-903b-2cead0b7ece1'
CLASS_QUERY = f'https://calendar.mywellness.com/v2/enduser/class/Search?eventTypes=Class&facilityId={FACILITY_ID}'
OPENING_TIME = datetime.time(hour=6, minute=1)
OPENING_DELTA = datetime.timedelta(days=5)


def get_classes_between_dates(date_from, date_to):
    """
    Get class between dates
    """
    date_from = date_from.strftime('%Y-%m-%d')
    date_to = date_to.strftime('%Y-%m-%d')
    url = f'{CLASS_QUERY}&fromDate={date_from}&toDate={date_to}'
    response = requests.get(url)
    classes_info = json.loads(response.text)
    return {(i['name'], i['actualizedStartDateTime']): i['id'] for i in classes_info}


def today_classes():
    """
    Get today classes
    """
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    return get_classes_between_dates(today, tomorrow)


def today_opening_classes():
    """
    Get today classes
    """
    today = datetime.datetime.now()
    opening = today + OPENING_DELTA
    opening_tomorrow = opening + datetime.timedelta(days=1)
    return get_classes_between_dates(opening, opening_tomorrow)

