from auto_book import utils
import json
import datetime

if __name__ == "__main__":
    booked_today = False

    with open('classes_to_book.json') as f:
        classes_to_book = json.load(f)

    now = datetime.datetime.now()
    opening = utils.opening(now)
    while True:
        # Block until the next opening time
        while now < opening:
            now = datetime.datetime.now()
        day = now.weekday()

        if day in classes_to_book:
            bookings = classes_to_book[day]
            opening_classes = utils.today_opening_classes()

            # Book classes
            for booking in bookings:
                slot_pk = (booking['class'], booking['time'])
                if slot_pk in opening_classes:
                    utils.book(utils.USER_ID, opening_classes[slot_pk], booking['time'])

        opening += datetime.timedelta(days=1)
