import getpass
import calendar
import requests
from datetime import datetime, timedelta
import json
import random

# Mywellness API
URL = 'https://calendar.mywellness.com/v2/enduser/class/'
SERVICE_URL = 'https://services.mywellness.com/Application/EC1D38D7-D359-48D0-A60C-D8C0B8FB9DF9/'
FACILITY_ID = 'dbf12cf8-3674-4daf-903b-2cead0b7ece1'
FACILITY_QUERY = f'Search?eventTypes=Class&facilityId={FACILITY_ID}'
BOOKING_QUERY = 'Book'
LOGIN_QUERY = 'Login'

# Datetime constants
OPENING_DELTA = timedelta(days=5)
ONE_MINUTE = timedelta(minutes=1)
THREE_MINUTES = timedelta(minutes=3)
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
TOLERANCE = timedelta(hours=1, minutes=30)

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

# Default path to booking file
if '/' in __file__:
    CLASSES_TO_BOOK = __file__[__file__.rfind('/') + 1] + 'classes_to_book.json'
elif '\\' in __file__:
    CLASSES_TO_BOOK = __file__[__file__.rfind('\\') + 1] + 'classes_to_book.json'
else:
    CLASSES_TO_BOOK = 'classes_to_book.json'


def classes_between_dates(date_from, date_to):
    """
    Get all class info between two dates.
    :param date_from: The date to start from.
    :param date_to: The date to end at.
    :return: A list of tuples containing the (name, datetime, id) of the classes between the two dates.
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
    Log in to the MyWellness website.
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


def book_classes_today(username, password, bookings, tol=TOLERANCE):
    """
    Book classes for today.
    :param username: User's username.
    :param password: User's password.
    :param bookings: The classes to book.
    :param tol: The tolerance of the booking times.
    """
    user_id, token = login(username, password)
    date_str = f'{now + OPENING_DELTA:%Y%m%d}'
    for class_name, class_time, class_id in today_opening_classes():
        if any(class_name == book_name and abs(class_time - datetime.combine(class_time, book_time.time())) <= tol
               for book_name, book_time in bookings):
            book(user_id, class_id, token, date_str)


if __name__ == "__main__":
    # Validate login credentials
    username, password = input('Username (Email): '), getpass.getpass('Password: ')
    while not login(username, password):
        print('Invalid username or password.')
        username, password = input('Username (Email): '), getpass.getpass('Password: ')
    print('Login successful')

    # Get opening time
    now = datetime.now()
    opening = now.replace(hour=6, minute=0, second=0, microsecond=0)
    opening = random_date_between(opening + ONE_MINUTE, opening + THREE_MINUTES)
    while True:
        try:
            # Block until the next opening time
            while now < opening:
                now = datetime.now()

            # Get classes to book
            with open(CLASSES_TO_BOOK) as f:
                bookings = json.load(f)
            daily_bookings = {d: [(i['class'], datetime.strptime(i['time'], TIME_FORMAT)) for i in info]
                              for d, info in bookings.items()}

            # Book classes opening today
            day = calendar.day_name[(opening + OPENING_DELTA).weekday()].lower()
            if day in daily_bookings:
                book_classes_today(username, password, daily_bookings[day])

            # Push opening to next opening time
            opening += timedelta(days=1)
            opening = opening.replace(hour=6, minute=0, second=0, microsecond=0)
            opening = random_date_between(opening + ONE_MINUTE, opening + THREE_MINUTES)

        except json.JSONDecodeError as e:
            print(f'Cannot read file at {CLASSES_TO_BOOK}. {e}')
        except FileExistsError as e:
            print(f'Cannot find file {CLASSES_TO_BOOK} {e}')
