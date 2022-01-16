import calendar
import requests
from datetime import datetime, timedelta
import json
import random
import os

# Mywellness API
URL = 'https://calendar.mywellness.com/v2/enduser/class/'
SERVICE_URL = 'https://services.mywellness.com/Application/EC1D38D7-D359-48D0-A60C-D8C0B8FB9DF9/'
FACILITY_ID = 'dbf12cf8-3674-4daf-903b-2cead0b7ece1'
FACILITY_QUERY = f'Search?eventTypes=Class&facilityId={FACILITY_ID}'
BOOKING_QUERY = 'Book'
LOGIN_QUERY = 'Login'

# Request headers
HEADERS = {
    'accept': '*/*',
    'content-type': 'application/json',
    'origin': 'https://widgets.mywellness.com',
    'referer': 'https://widgets.mywellness.com/',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'x-mwapps-appid': 'EC1D38D7-D359-48D0-A60C-D8C0B8FB9DF9',
    'x-mwapps-client': 'enduserweb',
    'x-mwapps-clientversion': '1.3.3-1096,enduserweb'
}

# Datetime constants
OPENING_DELTA = timedelta(days=5)
ONE_MINUTE = timedelta(minutes=1)
THREE_MINUTES = timedelta(minutes=3)
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

# Default path to booking file
CLASSES_TO_BOOK = f'{os.path.dirname(__file__)}\\classes_to_book.json'


def classes_between_dates(date_from, date_to):
    """
    Get all class info between and including two dates.
    :param date_from: The date to start from.
    :param date_to: The date to end at.
    :return: A list of tuples containing the (name, datetime, id) of the classes between and including the two dates.
    """
    url = f'{URL}{FACILITY_QUERY}&fromDate={date_from:%Y-%m-%d}&toDate={date_to:%Y-%m-%d}'
    response = requests.get(url)
    cls_info = json.loads(response.text)
    return [(i['name'], datetime.strptime(i['actualizedStartDateTime'], DATETIME_FORMAT), i['id']) for i in cls_info]


def random_date_between(date_from, date_to):
    """
    Get a random date between two dates.
    :param date_from: The date to start from.
    :param date_to: The date to end at.
    :return: A datetime between the two dates.
    """
    delta = date_to - date_from
    int_delta = (delta.days * 86400) + delta.seconds
    random_second = random.randint(0, int_delta)
    return date_from + timedelta(seconds=random_second)


def today_opening_classes():
    """
    Get all classes that are open today.
    :return: A list of tuples containing the (name, datetime, id) of the classes today.
    """
    opening = datetime.now() + OPENING_DELTA
    return classes_between_dates(opening, opening)


def today_opening_datetime():
    """
    Get the opening datetime of today.
    :return: The opening datetime of today.
    """
    return (datetime.now() + OPENING_DELTA).replace(hour=6, minute=0, second=0, microsecond=0)


def book(user_id, class_id, token, date):
    """
    Book a class.
    :param user_id: The id of the user booking.
    :param class_id: The id of the class to book.
    :param date: A string representing the date to book the class.
    :param token: The authentication token for the session.
    """
    headers = HEADERS.copy()
    headers['authorization'] = f'Bearer {token}'
    requests.post(
        headers=headers,
        url=f'{URL}{BOOKING_QUERY}',
        json={'userId': user_id, 'classId': class_id, 'partitionDate': int(date)},
    )


def login(username, password):
    """
    Login to the MyWellness website.
    :param username: User's username.
    :param password: User's password.
    :return: The user's id and authentication token for the session.
    """
    response = requests.post(
        headers=HEADERS,
        url=f'{SERVICE_URL}/{LOGIN_QUERY}',
        json={"username": username, "password": password, "keepMeLoggedIn": False},
    )
    login_info = json.loads(response.text)
    return (login_info['data']['userContext']['id'], login_info['token']) if 'data' in login_info else None


def book_classes_today(username, password, bookings, tol):
    """
    Book classes for today.
    :param username: User's username.
    :param password: User's password.
    :param bookings: The classes to book.
    :param tol: The tolerance of the booking times.
    """
    user_id, token = login(username, password)
    date_str = f'{datetime.now() + OPENING_DELTA:%Y%m%d}'
    for class_name, class_time, class_id in today_opening_classes():
        if any(class_name == book_name and abs(class_time - datetime.combine(class_time, book_time.time())) <= tol
               for book_name, book_time in bookings):
            book(user_id, class_id, token, date_str)


def book_class_on_opening(username, password, opening, booking_file, tol):
    """
    Book classes on opening.
    :param username: User's username.
    :param password: User's password.
    :param opening: The opening time.
    :param booking_file: THe json file with the booking info.
    :param tol: The time tolerance around booking.
    """
    # Get classes to book
    with open(booking_file) as f:
        bookings = json.load(f)
    # Check if there are any bookings today
    day = calendar.day_name[(opening + OPENING_DELTA).weekday()].lower()
    if day not in bookings:
        return
    # Block until opening time
    now = datetime.now()
    while now < opening:
        now = datetime.now()
    # Book classes
    today_bookings = [(i['class'], datetime.strptime(i['time'], TIME_FORMAT)) for i in bookings[day]]
    book_classes_today(username, password, today_bookings, tol)
