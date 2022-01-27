from datetime import timedelta
import random
import os


# Datetime constants
ONE_MINUTE = timedelta(minutes=1)
THREE_MINUTES = timedelta(minutes=3)
FORTNIGHT = timedelta(days=14)
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

# Default path to booking file
CLASSES_TO_BOOK = os.path.join(os.path.dirname(__file__), 'classes_to_book.json')


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
