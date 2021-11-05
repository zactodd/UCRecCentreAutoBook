import getpass
import calendar
import requests
import datetime
import json

URL = 'https://calendar.mywellness.com/v2/enduser/class/'
SERVICE_URL = 'https://services.mywellness.com/Application/EC1D38D7-D359-48D0-A60C-D8C0B8FB9DF9/'
FACILITY_ID = 'dbf12cf8-3674-4daf-903b-2cead0b7ece1'
FACILITY_QUERY = f'Search?eventTypes=Class&facilityId={FACILITY_ID}'
BOOKING_QUERY = 'Book'
LOGIN_QUERY = 'Login'

OPENING_DELTA = datetime.timedelta(days=5)

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

CLASSES_TO_BOOK = __file__[:__file__.rindex('/') + 1] + 'classes_to_book.json'


def get_classes_between_dates(date_from, date_to):
    date_from = date_from.strftime('%Y-%m-%d')
    date_to = date_to.strftime('%Y-%m-%d')
    url = f'{URL}{FACILITY_QUERY}&fromDate={date_from}&toDate={date_to}'
    response = requests.get(url)
    classes_info = json.loads(response.text)
    return {(i['name'], i['actualizedStartDateTime'][-8:]): i['id'] for i in classes_info}


def today_opening_classes():
    today = datetime.datetime.now()
    opening = today + OPENING_DELTA
    opening_tomorrow = opening + datetime.timedelta(days=1)
    return get_classes_between_dates(opening, opening_tomorrow)


def book(user_id, class_id, dt, token):
    headers = HEADERS.copy()
    headers['authorization'] = f'Bearer {token}'
    requests.post(
        headers=headers,
        url=f'{URL}{BOOKING_QUERY}',
        json={'userId': user_id, 'classId': class_id, 'partitionDate': dt},
    )


def login(username, password):
    response = requests.post(
        headers=HEADERS,
        url=f'{SERVICE_URL}/{LOGIN_QUERY}',
        json={"username": username, "password": password, "keepMeLoggedIn": False},
    )
    login_info = json.loads(response.text)
    data = login_info['data']['facilities'][0]
    return data['id'], login_info['token']


if __name__ == "__main__":
    # Get classes
    with open(CLASSES_TO_BOOK) as f:
        classes_to_book = json.load(f)

    valid_login = False
    while not valid_login:
        try:
            username = input('Username (Email): ')
            password = getpass.getpass('Password: ')
            facility_id, token = login(username, password)
            valid_login = True
        except:
            print('Invalid username or password.')
    print('Login successful.')

    now = datetime.datetime.now()
    opening = now.replace(hour=6, minute=1)

    while True:
        try:
            # Block until the next opening time
            while now < opening:
                now = datetime.datetime.now()

            user_id, token = login(username, password)

            day = calendar.day_name[(now + OPENING_DELTA).weekday()].lower()
            if day in classes_to_book:
                bookings = classes_to_book[day]
                opening_classes = today_opening_classes()

                # Book classes
                for booking in bookings:
                    slot_pk = (booking['class'], booking['time'])
                    if slot_pk in opening_classes:
                        time_str = int((now + OPENING_DELTA).strftime('%Y%m%d'))
                        book(user_id, opening_classes[slot_pk], time_str, token)
            opening += datetime.timedelta(days=1)
        except Exception as e:
            print(f'Error {e}')
