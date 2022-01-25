import argparse
from datetime import datetime, timedelta
import json
import sys
import utils
import booking
import calender_notification

# Script arguments
parser = argparse.ArgumentParser()
parser.add_argument('username', type=str, help='Gym username.')
parser.add_argument('password', type=str, help='Gym password.')
parser.add_argument('-f', '--bookings', type=str,
                    help='File path of class to book json.', default=utils.CLASSES_TO_BOOK)
parser.add_argument('-t', '--tolerance',
                    type=int, help='Tolerance between booking time and class time.', default=15)
parser.add_argument('-d', '--random_delay',
                    type=bool, help='If to randomly delay the bookings.', default=False, const=True, nargs='?')
parser.add_argument('-c', '--calendar_notification',
                    type=bool, help='If to send notification on booking.', default=False, const=True, nargs='?')


if __name__ == "__main__":
    kwargs = vars(parser.parse_args(sys.argv[1:]))

    username, password = kwargs['username'], kwargs['password']
    assert booking.login(username, password), 'Invalid username or password.'

    booking_file = kwargs['bookings']
    random_delay = kwargs['random_delay']
    calendar_notification = kwargs['calendar_notification']
    tolerance = timedelta(minutes=kwargs['tolerance'])

    # Opening time
    opening = datetime.now().replace(hour=6, minute=0, second=0)
    if random_delay:
        opening = utils.random_date_between(opening + utils.ONE_MINUTE, opening + utils.THREE_MINUTES)

    # Booking file
    with open(booking_file, 'r') as f:
        bookings = json.load(f)

    # Book classes on opening
    booked_classes_info = booking.book_class_on_opening(username, password, opening, bookings, tolerance)

    # Send notification for booked classes
    if calendar_notification and booked_classes_info is not None:
        calender_notification.send_calendar_notification(booked_classes_info)
