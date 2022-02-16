from datetime import datetime, timedelta
from collections import defaultdict
import json
import calendar
import requests
import utils
import attr

# UC RecCentre ID
FACILITY_ID = 'dbf12cf8-3674-4daf-903b-2cead0b7ece1'

# Mywellness API
_MYWELLNESS_URL = 'https://calendar.mywellness.com/v2/enduser/class/'
_SERVICE_URL = 'https://services.mywellness.com/Application/EC1D38D7-D359-48D0-A60C-D8C0B8FB9DF9/'
_FACILITY_QUERY = f'Search?eventTypes=Class&facilityId={FACILITY_ID}'
_BOOKING_QUERY = 'Book'
_LOGIN_QUERY = 'Login'

# Request headers
_HEADERS = {
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

_NAMED_TIMES = {
    'morning': ('05:30:00', '12:00:00'),
    'afternoon': ('12:00:00', '18:30:00'),
    'evening': ('18:30:00', '23:59:59'),
    'early morning': ('5:30:00', '8:30:00'),
    'late morning': ('8:30:00', '12:00:00'),
    'midday': ('11:00:00', '13:00:00'),
    'early afternoon': ('12:00:00', '15:30:00'),
    'late afternoon': ('15:30:00', '18:30:00'),
    'early evening': ('18:30:00', '21:00:00'),
    'late evening': ('21:00:00', '23:59:59'),
}

# Datetime constants
OPENING_DELTA = timedelta(days=5)


@attr.s
class ClassInfo:
    id: str = attr.ib()
    name: str = attr.ib()
    room: str = attr.ib()
    is_booked: bool = attr.ib(converter=bool)
    date: datetime = attr.ib(converter=utils.to_datetime)
    start: datetime = attr.ib(converter=utils.to_datetime)
    end: datetime = attr.ib(converter=utils.to_datetime)


def classes_between_dates(date_from, date_to, token=None):
    """
    Get all class info between and including two dates.
    :param date_from: The date to start from.
    :param date_to: The date to end at.
    :param token: The authentication token for the session.
    :return: ClassInfo of the classes between and including the two dates.
    """
    url = f'{_MYWELLNESS_URL}{_FACILITY_QUERY}&fromDate={date_from:%Y-%m-%d}&toDate={date_to:%Y-%m-%d}'
    if token:
        headers = _HEADERS.copy()
        headers['authorization'] = f'Bearer {token}'
        response = requests.get(headers=headers, url=url)
    else:
        response = requests.get(url=url)
    classes_json = json.loads(response.text)
    return [ClassInfo(c['id'], c['name'], c['room'], c['isParticipant'],
                      c['actualizedStartDateTime'], c['startDate'], c['endDate'])
            for c in classes_json]


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
    :return: ClassInfo of the classes opening today.
    """
    return (datetime.now() + OPENING_DELTA).replace(hour=6, minute=0, second=0, microsecond=0)


def upcoming_open_classes():
    """
    Get all classes that are open from today until the end of the week.
    :return: ClassInfo of the classes opening this week.
    """
    now = datetime.now()
    return classes_between_dates(datetime.now(), now + OPENING_DELTA)


def book(user_id, class_id, token, date):
    """
    Book a class.
    :param user_id: The id of the user booking.
    :param class_id: The id of the class to book.
    :param date: A datetime of class to book.
    :param token: The authentication token for the session.
    """
    headers = _HEADERS.copy()
    headers['authorization'] = f'Bearer {token}'
    requests.post(
        headers=headers,
        url=f'{_MYWELLNESS_URL}{_BOOKING_QUERY}',
        json={'userId': user_id, 'classId': class_id, 'partitionDate': int(f'{date:%Y%m%d}')},
    )


def login(username, password):
    """
    Login to the MyWellness website.
    :param username: User's username.
    :param password: User's password.
    :return: The user's id and authentication token for the session.
    """
    response = requests.post(
        headers=_HEADERS,
        url=f'{_SERVICE_URL}/{_LOGIN_QUERY}',
        json={"username": username, "password": password, "keepMeLoggedIn": False},
    )
    login_info = json.loads(response.text)
    return (login_info['data']['userContext']['id'], login_info['token']) if 'data' in login_info else None


def is_class_in_booking(class_name, class_time, bookings, tol):
    """
    Check if a class is in the booking list.
    :param class_name: Name of the class.
    :param class_time: Datetime of the class.
    :param bookings: List of bookings.
    :param tol: Time tolerance.
    :return: If the class is in the booking list.
    """
    for info in bookings:
        book_name, book_time_str = info['class'], info['time']
        if class_name != book_name:
            continue
        book_time_str = book_time_str.lower()
        if book_time_str in _NAMED_TIMES:
            min_time, max_time = _NAMED_TIMES[book_time_str]
            min_time = datetime.combine(class_time, datetime.strptime(min_time, utils.TIME_FORMAT).time())
            max_time = datetime.combine(class_time, datetime.strptime(max_time, utils.TIME_FORMAT).time())
        else:
            book_time = datetime.combine(class_time, datetime.strptime(book_time_str, utils.TIME_FORMAT).time())
            min_time = book_time - tol
            max_time = book_time + tol
        if min_time <= class_time <= max_time:
            return True
    return False


def book_classes(username, password, classes, bookings, tol):
    """
    Book classes.
    :param username: The user's username.
    :param password: The user's password.
    :param classes: The classes to book.
    :param bookings: The bookings to check against.
    :param tol: The time tolerance.
    :return: The bookings that were booked.
    """
    user_id, token = login(username, password)
    booked = []
    for c in classes:
        if is_class_in_booking(c.name, c.date, bookings, tol):
            book(user_id, c.id, token, c.date)
            booked.append(c)
    return booked

def block_til_opening(opening):
    """
    Block until opening.
    :param opening: The opening time.
    """
    now = datetime.now()
    while now < opening:
        now = datetime.now()


def book_class_on_opening(username, password, opening, bookings, tol, block_for_opening=True):
    """
    Book classes on opening.
    :param username: User's username.
    :param password: User's password.
    :param opening: The opening time.
    :param bookings: Classes with booking times.
    :param tol: The time tolerance around booking.
    :param block_for_opening: If the program should block for the opening.

    :return: The classes booked.
    """
    # Check if there are any bookings today
    day = calendar.day_name[(opening + OPENING_DELTA).weekday()].lower()
    if day not in bookings:
        return
    # Block until opening time
    if block_for_opening:
        block_til_opening(opening)
    # Book classes
    today_bookings = bookings[day]
    today_classes = today_opening_classes()
    return book_classes(username, password, today_classes, today_bookings, tol)



def book_upcoming_classes_on_opening(username, password, opening, bookings, tol, block_for_opening=True):
    """
    Book classes on that are open.
    :param username: User's username.
    :param password: User's password.
    :param opening: The opening time.
    :param bookings: Classes with booking times.
    :param tol: The time tolerance around booking.
    :param block_for_opening: If the program should block for the opening.
    :return: The classes booked.
    """
    if block_for_opening:
        block_til_opening(opening)

    classes_day = defaultdict(list)
    for c in upcoming_open_classes():
        if not c.is_booked:
            classes_day[calendar.day_name[c.date.weekday()].lower()].append(c)
    booked = []
    for day, day_classes in classes_day.items():
        day_bookings = bookings[day]
        booked.extend(book_classes(username, password, day_classes, day_bookings, tol))
    return booked


def special_classes(look_back_interval=utils.FORTNIGHT):
    """
    Get the special classes.
    :param look_back_interval: The time to uses to determine which classes are special.
    :return: A List of special classes.
    """
    yesterday = datetime.now() - timedelta(days=1)
    classes = classes_between_dates(yesterday - look_back_interval, yesterday)
    classes = {c.name for c in classes}
    open_classes = upcoming_open_classes()
    return [c for c in open_classes if c.name not in classes]


def book_special_classes(username, password):
    """
    Book special classes.
    :param username: User's username.
    :param password: User's password.
    :return: The classes booked.
    """
    classes = special_classes()
    user_id, token = login(username, password)
    for c in classes:
        book(user_id, c.id, token, c.date)
    return classes
