import getpass
import calendar
import requests
import datetime
import json
import random

URL = 'https://calendar.mywellness.com/v2/enduser/class/'
SERVICE_URL = 'https://services.mywellness.com/Application/EC1D38D7-D359-48D0-A60C-D8C0B8FB9DF9/'
FACILITY_ID = 'dbf12cf8-3674-4daf-903b-2cead0b7ece1'
FACILITY_QUERY = f'Search?eventTypes=Class&facilityId={FACILITY_ID}'
BOOKING_QUERY = 'Book'
LOGIN_QUERY = 'Login'

OPENING_DELTA = datetime.timedelta(days=5)
TEN_MINUTES = datetime.timedelta(minutes=10)
ONE_MINUTE = datetime.timedelta(minutes=1)
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
TOLERANCE = datetime.timedelta(hours=1, minutes=30)

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

CLASSES_TO_BOOK = __file__[:__file__.rindex('/' if "/" in __file__ else '\\') + 1] + 'classes_to_book.json'


def classes_between_dates(date_from, date_to):
    """
    GEt all class info between two dates.
    :param date_from: The date to start from.
    :param date_to: The date to end at.
    :return: A list of tuples containing the (name, datetime, id) of the classes between the two dates.
    """
    date_from = date_from.strftime('%Y-%m-%d')
    date_to = date_to.strftime('%Y-%m-%d')
    url = f'{URL}{FACILITY_QUERY}&fromDate={date_from}&toDate={date_to}'
    response = requests.get(url)
    classes_info = json.loads(response.text)
    return [(i['name'], datetime.datetime.strptime(i['actualizedStartDateTime'], DATETIME_FORMAT), i['id'])
            for i in classes_info]


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
    return date_from + datetime.timedelta(seconds=random_second)


def today_opening_classes():
    """
    Get all classes that are open today.
    :return: A list of tuples containing the (name, datetime, id) of the classes today.
    """
    today = datetime.datetime.now()
    opening = today + OPENING_DELTA
    opening_tomorrow = opening + datetime.timedelta(days=1)
    return classes_between_dates(opening, opening_tomorrow)


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
        json={'userId': user_id, 'classId': class_id, 'partitionDate': date},
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
    return login_info['data']['userContext']['id'], login_info['token'] if login_info else None


def book_classes_today(username, password, bookings, tol=TOLERANCE):
    """
    Book classes for today.
    :param username: User's username.
    :param password: User's password.
    :param bookings: The classes to book.
    :param tol: The tolerance of the booking times.
    """
    user_id, token = login(username, password)
    date_str = int((now + OPENING_DELTA).strftime('%Y%m%d'))
    for n, dt, idx in today_opening_classes():
        ct = dt.time()
        if any(n == m and bdt.time() - tol <= ct <= bdt.time() + tol for m, bdt in bookings):
            book(user_id, idx, token, date_str)


if __name__ == "__main__":
    # Validate login credentials
    username, password = input('Username (Email): '), getpass.getpass('Password: ')
    while login(username, password):
        username, password = input('Username (Email): '), getpass.getpass('Password: ')
        print('Invalid username or password.')
    print('Login successful')

    # Get opening time
    now = datetime.datetime.now()
    opening = now.replace(hour=6, minute=0, second=0, microsecond=0)
    opening = random_date_between(opening + ONE_MINUTE, opening + TEN_MINUTES)
    while True:
        try:
            # Block until the next opening time
            while now < opening:
                now = datetime.datetime.now()

            # Get classes to book
            with open(CLASSES_TO_BOOK) as f:
                bookings_json = json.load(f)
            daily_bookings = {d: [(i['class'], datetime.datetime.strptime(i['time'], TIME_FORMAT)) for i in info]
                              for d, info in bookings_json.items()}

            # Book classes opening today
            day = calendar.day_name[(now + OPENING_DELTA).weekday()].lower()
            if day in daily_bookings:
                book_classes_today(username, password, daily_bookings[day])

            # Push opening to next opening time
            opening += datetime.timedelta(days=1)
            opening = opening.replace(hour=6, minute=0, second=0, microsecond=0)
            opening = random_date_between(opening + ONE_MINUTE, opening + TEN_MINUTES)

        except json.JSONDecodeError as e:
            print(f'Cannot read file at {CLASSES_TO_BOOK}. {e}')
        except FileExistsError as e:
            print(f'Cannot find file {CLASSES_TO_BOOK} {e}')
