import requests
import datetime
import json

URL = f'https://calendar.mywellness.com/v2/enduser/class/'

with open('user_info.json') as f:
    USER_ID = json.load(f)['userId']

FACILITY_ID = 'dbf12cf8-3674-4daf-903b-2cead0b7ece1'
FACILITY_QUERY = f'Search?eventTypes=Class&facilityId={FACILITY_ID}'
BOOKING_QUERY = 'Book?_c=en-GB'
OPENING_TIME = datetime.time(hour=6, minute=1)
OPENING_DELTA = datetime.timedelta(days=5)

HEADERS = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer MjAyMTExMDQyMzA0MzB8ODIzZjY0NjJjZTQzNGQwODhmZmQ2YjM3M2NkYmQxZTB8ZWMxZDM4ZDdkMzU5NDhkMGE2MGNkOGMwYjhmYjlkZjl8MnxOZXcgWmVhbGFuZCBTdGFuZGFyZCBUaW1lfGVuLUdCfDU4MmRhNDJjNjI1MjQ1Y2NhOWQ1NGJmMDI4YjU0NjgyfHx8fDF8MXwwfDF8fHwwfDY0NnwwfGNvbS5teXdlbGxuZXNz0.2C0D2D6A20687C4E13DE8F21CAD2BA2ED17785C83DB3AD560B0AD323E71668D593510F23A0B2B7C7E85F8BADB8E548E48E5B2898239D781C7D56BA3477933AA2'
}


def get_classes_between_dates(date_from, date_to):
    date_from = date_from.strftime('%Y-%m-%d')
    date_to = date_to.strftime('%Y-%m-%d')
    url = f'{URL}{FACILITY_QUERY}&fromDate={date_from}&toDate={date_to}'
    response = requests.get(url)
    classes_info = json.loads(response.text)
    return {(i['name'], i['actualizedStartDateTime'][-10:]): i['id'] for i in classes_info}


def today_classes():
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    return get_classes_between_dates(today, tomorrow)


def today_opening_classes():
    today = datetime.datetime.now()
    opening = today + OPENING_DELTA
    opening_tomorrow = opening + datetime.timedelta(days=1)
    return get_classes_between_dates(opening, opening_tomorrow)


def opening(dt):
    return dt.replace(hour=OPENING_TIME.hour, minute=OPENING_TIME.minute)


def book(user_id, class_id, dt):
    requests.post(
        headers=HEADERS,
        url=f'{URL}{BOOKING_QUERY}',
        json={'userId': user_id, 'classId': class_id, 'partitionDate': dt},
    )
