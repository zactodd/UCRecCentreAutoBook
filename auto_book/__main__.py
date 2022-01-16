import argparse
from datetime import datetime, timedelta
from itertools import accumulate, repeat
import sys
import utils

# Script arguments
parser = argparse.ArgumentParser()
parser.add_argument('username', type=str, help='Gym username.')
parser.add_argument('password', type=str, help='Gym password.')
parser.add_argument('-f', '--bookings', type=str,
                    help='File path of class to book json.', default=utils.CLASSES_TO_BOOK)
parser.add_argument('-t', '--tolerance',
                    type=int, help='Tolerance between booking time and class time.', default=90)
parser.add_argument('-r', '--repeat_daily',
                    type=bool, help='If to repeat the script daily.', default=False, const=True, nargs='?')
parser.add_argument('-d', '--random_delay',
                    type=bool, help='If to randomly delay the bookings.', default=False, const=True, nargs='?')


if __name__ == "__main__":
    kwargs = vars(parser.parse_args(sys.argv[1:]))

    username, password = kwargs['username'], kwargs['password']
    assert utils.login(username, password), 'Invalid username or password.'

    repeat_booking = kwargs['repeat']
    booking_file = kwargs['bookings']
    random_delay = kwargs['random_delay']
    tolerance = timedelta(minutes=kwargs['tolerance'])

    # Opening times
    openings = accumulate(repeat(timedelta(days=1)), initial=datetime.now().replace(hour=6, minute=0, second=0))
    if random_delay:
        openings = map(lambda dt: utils.random_date_between(dt + utils.ONE_MINUTE, dt + utils.THREE_MINUTES), openings)

    # Book classes on opening
    utils.book_class_on_opening(username, password, next(openings), booking_file, tolerance)
    
    if repeat_booking:
        for opening in openings:
            utils.book_class_on_opening(username, password, opening, booking_file, tolerance)
